from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import fitz
except ImportError as exc:
    raise SystemExit("PyMuPDF is required. Run: pip install -r requirements.txt") from exc

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
DATA_DIR = STATIC / "data"
TASK_DIR = STATIC / "generated" / "tasks"
ANSWER_DIR = STATIC / "generated" / "answers"
PREVIEW_DIR = STATIC / "generated" / "previews"

HEADING_PATTERNS = [
    re.compile(r"\b[ÜU]lesanne\s+nr\.?\s*(\d+)", re.I),
    re.compile(r"\b[ÜU]lesanne\s+(\d+)", re.I),
    re.compile(r"\bYlesanne\s+(\d+)", re.I),
]
NUMBER_PATTERNS = [
    re.compile(r"^\s*(\d{1,2})\.\s", re.I),
]


@dataclass(frozen=True)
class Start:
    number: int
    page_index: int
    x: float
    y: float
    heading: str
    part: int | None = None


def public_path(path: Path) -> str:
    return "/" + path.relative_to(STATIC).as_posix()


def load_exams() -> list[dict[str, Any]]:
    path = DATA_DIR / "exams.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def find_task_number(text: str, allow_number_only: bool) -> int | None:
    compact = " ".join(text.split())
    patterns = HEADING_PATTERNS + (NUMBER_PATTERNS if allow_number_only else [])
    for pattern in patterns:
        match = pattern.search(compact)
        if match:
            number = int(match.group(1))
            if 1 <= number <= 30:
                return number
    return None


def detect_starts(document: fitz.Document, allow_number_only: bool = False) -> list[Start]:
    starts_by_key: dict[tuple[int, int, int | None], Start] = {}
    current_part: int | None = None
    for page_index in range(document.page_count):
        page = document.load_page(page_index)
        page_dict = page.get_text("dict", sort=True)
        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                line_text = " ".join("".join(span.get("text", "") for span in line.get("spans", [])).split())
                if not line_text:
                    continue
                x0, y0, _x1, _y1 = line["bbox"]
                upper_text = line_text.upper()
                if "II OSA" in upper_text:
                    current_part = 2
                elif "I OSA" in upper_text:
                    current_part = 1
                number = find_task_number(line_text, allow_number_only)
                if number is None:
                    continue
                if line_text.startswith("Hindaja Ülesanne") and page.rect.width > 800:
                    x0 = page.rect.width / 2 + 47
                if x0 > page.rect.width * 0.75:
                    continue
                key = (page_index, number, current_part)
                start = Start(number=number, page_index=page_index, x=float(x0), y=float(y0), heading=line_text[:120], part=current_part)
                current = starts_by_key.get(key)
                if current is None or start.y < current.y:
                    starts_by_key[key] = start

        blocks = page.get_text("blocks", sort=True)
        for block in blocks:
            if len(block) < 5:
                continue
            x0, y0, _x1, _y1, text = block[:5]
            block_text = " ".join(str(text).split())
            upper_text = block_text.upper()
            if "II OSA" in upper_text:
                current_part = 2
            elif "I OSA" in upper_text:
                current_part = 1
            number = find_task_number(block_text, allow_number_only and not starts_by_key)
            if number is None:
                continue
            if block_text.startswith("Hindaja Ülesanne") and page.rect.width > 800:
                x0 = page.rect.width / 2 + 47
            if x0 > page.rect.width * 0.75:
                continue
            key = (page_index, number, current_part)
            start = Start(number=number, page_index=page_index, x=float(x0), y=float(y0), heading=block_text[:120], part=current_part)
            current = starts_by_key.get(key)
            if current is None:
                starts_by_key[key] = start
    ordered = sorted(starts_by_key.values(), key=lambda item: (item.page_index, item.y, item.number))
    unique_position_starts: list[Start] = []
    seen_positions: set[tuple[int, int, int]] = set()
    for start in ordered:
        position_key = (start.page_index, start.number, round(start.y))
        if position_key in seen_positions:
            continue
        seen_positions.add(position_key)
        unique_position_starts.append(start)

    by_number: dict[tuple[int | None, int], Start] = {}
    for start in unique_position_starts:
        by_number.setdefault((start.part, start.number), start)
    return sorted(by_number.values(), key=lambda item: (item.page_index, item.y, item.number))


def is_lisaleht_page(page: fitz.Page) -> bool:
    text = " ".join(page.get_text().split()).upper()
    return " LISALEHT" in f" {text}" or text.startswith("LISALEHT")


def is_header_only_page(page: fitz.Page) -> bool:
    text = " ".join(page.get_text().split()).upper()
    return len(text) < 80 and "ÜLESANNE" not in text and "YLESANNE" not in text


def same_column(page: fitz.Page, first: Start, second: Start | None) -> bool:
    if second is None or first.page_index != second.page_index:
        return False
    if page.rect.width <= 800:
        return True
    midpoint = page.rect.width / 2
    return (first.x < midpoint) == (second.x < midpoint)


def horizontal_bounds(page: fitz.Page, start: Start, *, full_width: bool) -> tuple[float, float]:
    rect = page.rect
    if full_width or rect.width <= 800:
        return min(30, rect.width - 2), max(31, rect.width - 30)

    midpoint = rect.width / 2
    if start.x < midpoint:
        return 30, midpoint - 30
    return midpoint + 30, rect.width - 30


def crop_for_page(page: fitz.Page, start: Start, y0: float, y1: float, *, full_width: bool, enforce_min_height: bool) -> fitz.Rect:
    rect = page.rect
    x0, x1 = horizontal_bounds(page, start, full_width=full_width)
    top = min(max(0, y0 - 8), max(0, rect.height - 2))
    desired_bottom = y1 - 10
    content_bottom = non_grid_content_bottom(page, x0, x1, top, desired_bottom)
    grid_top = detect_grid_top(page, x0, x1, max(top, content_bottom + 8), desired_bottom)
    if grid_top is not None and grid_top > top + 60:
        desired_bottom = min(desired_bottom, grid_top - 6)
    if enforce_min_height:
        desired_bottom = max(top + 80, desired_bottom)
    bottom = min(rect.height, desired_bottom)
    if bottom <= top + 1:
        top = 0
        bottom = rect.height
    return fitz.Rect(x0, top, x1, bottom)


def leading_image_rect(page: fitz.Page, start: Start, *, full_width: bool) -> fitz.Rect | None:
    x0, x1 = horizontal_bounds(page, start, full_width=full_width)
    leading: fitz.Rect | None = None
    page_dict = page.get_text("dict", sort=True)
    for block in page_dict.get("blocks", []):
        if block.get("type") != 1:
            continue
        bx0, by0, bx1, by1 = block.get("bbox", (0, 0, 0, 0))
        if bx1 < x0 or bx0 > x1:
            continue
        if by0 >= start.y or by1 < start.y - 4:
            continue
        if start.y - by0 > 90:
            continue
        rect = fitz.Rect(bx0, by0, bx1, by1)
        if leading is None or rect.y0 < leading.y0:
            leading = rect
    return leading


def visual_start_y(page: fitz.Page, start: Start, *, full_width: bool) -> float:
    """Include figures that are laid out beside a task heading but start above it."""
    leading = leading_image_rect(page, start, full_width=full_width)
    return float(leading.y0) if leading is not None else start.y


def is_light_gray(color: Any) -> bool:
    if not color or len(color) < 3:
        return False
    return min(color[:3]) > 0.72 and max(color[:3]) - min(color[:3]) < 0.08


def detect_grid_top(page: fitz.Page, x0: float, x1: float, y0: float, y1: float) -> float | None:
    horizontal: dict[int, int] = {}
    vertical: list[tuple[float, float]] = []

    for drawing in page.get_drawings():
        rect = drawing.get("rect")
        if rect is None or not is_light_gray(drawing.get("color")):
            continue
        if rect.x1 < x0 or rect.x0 > x1 or rect.y1 < y0 or rect.y0 > y1:
            continue
        width = rect.x1 - rect.x0
        height = rect.y1 - rect.y0
        if height <= 1 and width >= 8:
            key = round(rect.y0)
            horizontal[key] = horizontal.get(key, 0) + 1
        elif width <= 1 and height >= 8:
            vertical.append((rect.y0, rect.y1))

    for key in sorted(horizontal):
        if horizontal[key] < 8:
            continue
        vertical_at_row = sum(1 for top, bottom in vertical if top <= key + 2 and bottom >= key + 8)
        if vertical_at_row >= 8:
            return float(key)

    return None


def non_grid_content_bottom(page: fitz.Page, x0: float, x1: float, y0: float, y1: float) -> float:
    bottom = y0
    usable_bottom = min(y1, page.rect.height - 60)
    for block in page.get_text("blocks", sort=True):
        if len(block) < 5:
            continue
        bx0, by0, bx1, by1, text = block[:5]
        if by1 < y0 or by0 > usable_bottom or bx1 < x0 or bx0 > x1:
            continue
        block_text = " ".join(str(text).split())
        if block_text and block_text not in {"Hindaja"}:
            bottom = max(bottom, float(by1))

    for drawing in page.get_drawings():
        rect = drawing.get("rect")
        if rect is None or is_light_gray(drawing.get("color")):
            continue
        if drawing.get("color") is None:
            continue
        if rect.width > page.rect.width * 0.9 and rect.height > page.rect.height * 0.9:
            continue
        if rect.y1 < y0 or rect.y0 > usable_bottom or rect.x1 < x0 or rect.x0 > x1:
            continue
        width = rect.x1 - rect.x0
        height = rect.y1 - rect.y0
        if width <= 2 and height > 250:
            continue
        if height <= 2 and width > 350:
            continue
        if width > 2 or height > 2:
            bottom = max(bottom, float(rect.y1))

    return bottom


def render_clip(page: fitz.Page, clip: fitz.Rect, target: Path) -> None:
    pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=clip, alpha=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    pixmap.save(target)


def render_full_page(page: fitz.Page, target: Path) -> tuple[dict[str, float], str]:
    rect = page.rect
    render_clip(page, rect, target)
    crop = {"x0": rect.x0, "y0": rect.y0, "x1": rect.x1, "y1": rect.y1}
    return crop, public_path(target)


def crop_pieces(
    document: fitz.Document,
    start: Start,
    next_start: Start | None,
    directory: Path,
    prefix: str,
    *,
    full_width: bool = False,
    boundary_padding: float = 0,
) -> tuple[list[dict[str, Any]], list[str]]:
    pieces: list[dict[str, Any]] = []
    images: list[str] = []
    start_page = document.load_page(start.page_index)
    effective_next = next_start if next_start and next_start.page_index >= start.page_index else None
    if start_page.rect.width > 800 and effective_next is not None:
        if effective_next.page_index != start.page_index and not same_column(start_page, start, effective_next):
            effective_next = None

    if effective_next is None:
        end_page = start.page_index if start_page.rect.width > 800 else document.page_count - 1
    else:
        end_page = effective_next.page_index

    for page_index in range(start.page_index, end_page + 1):
        page = document.load_page(page_index)
        if page_index != start.page_index and (is_lisaleht_page(page) or is_header_only_page(page)):
            continue
        if page_index == start.page_index:
            y0 = visual_start_y(page, start, full_width=full_width)
        else:
            y0 = 0

        boundary_on_page = None
        if effective_next and page_index == effective_next.page_index:
            if page_index != start.page_index or same_column(page, start, effective_next):
                boundary_on_page = effective_next

        if boundary_on_page and page_index == boundary_on_page.page_index:
            y1 = boundary_on_page.y + boundary_padding
        else:
            y1 = page.rect.height - 30

        ending_at_next_start = boundary_on_page is not None and page_index == boundary_on_page.page_index
        if ending_at_next_start and page_index != start.page_index and y1 < 120:
            continue

        clip = crop_for_page(page, start, y0, y1, full_width=full_width, enforce_min_height=not ending_at_next_start)
        image_path = directory / f"{prefix}-p{page_index + 1}.png"
        render_clip(page, clip, image_path)
        crop = {"x0": clip.x0, "y0": clip.y0, "x1": clip.x1, "y1": clip.y1}
        pieces.append({"page": page_index + 1, "crop": crop, "image": public_path(image_path)})
        images.append(public_path(image_path))
    return pieces, images


def answer_page_pieces(
    document: fitz.Document,
    start: Start,
    next_start: Start | None,
    directory: Path,
    prefix: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    pieces: list[dict[str, Any]] = []
    images: list[str] = []
    end_page = (next_start.page_index - 1) if next_start and next_start.page_index > start.page_index else start.page_index
    end_page = min(max(start.page_index, end_page), document.page_count - 1)

    for page_index in range(start.page_index, end_page + 1):
        page = document.load_page(page_index)
        image_path = directory / f"{prefix}-p{page_index + 1}.png"
        crop, image = render_full_page(page, image_path)
        pieces.append({"page": page_index + 1, "crop": crop, "image": image})
        images.append(image)

    return pieces, images


def split_answer_markers(text: str) -> list[tuple[int, int]]:
    markers: list[tuple[int, int]] = []
    for match in re.finditer(r"\b(?:ÜL\s*)?(I{1,2})_(\d{1,2})\b", text, re.I):
        part = 2 if match.group(1).upper() == "II" else 1
        markers.append((part, int(match.group(2))))
    return markers


def detect_answer_table_starts(document: fitz.Document) -> dict[tuple[int, int], Start]:
    starts: dict[tuple[int, int], Start] = {}
    duplicates: dict[tuple[int, int], list[Start]] = {}
    for page_index in range(document.page_count):
        page = document.load_page(page_index)
        for block in page.get_text("blocks", sort=True):
            if len(block) < 5:
                continue
            x0, y0, _x1, _y1, text = block[:5]
            block_text = " ".join(str(text).split())
            for part, number in split_answer_markers(block_text):
                key = (part, number)
                start = Start(number=number, page_index=page_index, x=float(x0), y=float(y0), heading=block_text[:120], part=part)
                if key in starts:
                    duplicates.setdefault(key, [starts[key]]).append(start)
                else:
                    starts[key] = start
    if (2, 5) not in starts and (2, 4) in duplicates and len(duplicates[(2, 4)]) > 1:
        duplicate = sorted(duplicates[(2, 4)], key=lambda item: (item.page_index, item.y))[-1]
        starts[(2, 5)] = Start(number=5, page_index=duplicate.page_index, x=duplicate.x, y=duplicate.y, heading=duplicate.heading, part=2)
    return starts


def answer_table_pieces(
    document: fitz.Document,
    start: Start,
    next_start: Start | None,
    directory: Path,
    prefix: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    page = document.load_page(start.page_index)
    rect = page.rect
    next_y = next_start.y if next_start and next_start.page_index == start.page_index else rect.height - 30
    top = max(0, start.y - 8)
    bottom = min(rect.height, max(top + 34, next_y - 4))
    x0 = max(0, start.x - 8)
    clip = fitz.Rect(x0, top, rect.width - 30, bottom)
    image_path = directory / f"{prefix}-answer-p{start.page_index + 1}.png"
    render_clip(page, clip, image_path)
    crop = {"x0": clip.x0, "y0": clip.y0, "x1": clip.x1, "y1": clip.y1}
    image = public_path(image_path)
    return [{"page": start.page_index + 1, "crop": crop, "image": image}], [image]


def dark_pixel(data: bytes, index: int, threshold: int) -> bool:
    return max(data[index], data[index + 1], data[index + 2]) < threshold


def horizontal_pixel_lines(page: fitz.Page) -> list[int]:
    pixmap = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    width, height, channels = pixmap.width, pixmap.height, pixmap.n
    data = pixmap.samples
    rows: list[int] = []
    for y in range(height):
        dark_count = 0
        for x in range(50, min(width, 430)):
            index = (y * width + x) * channels
            if dark_pixel(data, index, 200):
                dark_count += 1
        if dark_count > 180:
            rows.append(y)

    groups: list[list[int]] = []
    for row in rows:
        if not groups or row > groups[-1][-1] + 1:
            groups.append([row])
        else:
            groups[-1].append(row)
    return [round(sum(group) / len(group)) for group in groups]


def label_pixel_count(page: fitz.Page, top: int, bottom: int) -> int:
    pixmap = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    width, channels = pixmap.width, pixmap.n
    data = pixmap.samples
    count = 0
    for y in range(top + 2, max(top + 2, bottom - 2)):
        for x in range(75, min(width, 175)):
            index = (y * width + x) * channels
            if dark_pixel(data, index, 90):
                count += 1
    return count


def detect_scanned_answer_rows(document: fitz.Document) -> dict[tuple[int, int], fitz.Rect]:
    if document.page_count == 0:
        return {}
    page = document.load_page(0)
    lines = horizontal_pixel_lines(page)
    if len(lines) < 10:
        return {}

    rows: list[tuple[int, int]] = []
    for top, bottom in zip(lines[1:], lines[2:]):
        if bottom <= top + 4:
            continue
        has_label = label_pixel_count(page, top, bottom) > 15
        if has_label:
            rows.append((top, bottom))
        elif rows:
            previous_top, _previous_bottom = rows[-1]
            rows[-1] = (previous_top, bottom)

    if len(rows) < 12:
        return {}

    keys = [(1, number) for number in range(1, 8)] + [(2, number) for number in range(1, 6)]
    result: dict[tuple[int, int], fitz.Rect] = {}
    for key, (top, bottom) in zip(keys, rows):
        result[key] = fitz.Rect(70, max(0, top - 2), min(page.rect.width, 390), min(page.rect.height, bottom + 2))
    return result


def is_black_fill(value: Any) -> bool:
    return bool(value) and len(value) >= 3 and max(value[:3]) < 0.12


def detect_drawn_answer_rows(document: fitz.Document) -> dict[tuple[int, int], fitz.Rect]:
    if document.page_count == 0:
        return {}
    page = document.load_page(0)
    line_segments_by_y: dict[int, list[fitz.Rect]] = {}

    for drawing in page.get_drawings():
        rect = drawing.get("rect")
        if rect is None or not is_black_fill(drawing.get("fill")):
            continue
        if rect.height > 1.5 or rect.width < 20:
            continue
        key = round(rect.y0)
        line_segments_by_y.setdefault(key, []).append(rect)

    table_lines: list[tuple[float, float, float]] = []
    for segments in line_segments_by_y.values():
        x0 = min(segment.x0 for segment in segments)
        x1 = max(segment.x1 for segment in segments)
        coverage = sum(segment.width for segment in segments)
        if coverage < 200 or x1 - x0 < 200:
            continue
        y = min(segment.y0 for segment in segments)
        table_lines.append((y, x0, x1))

    table_lines.sort(key=lambda item: item[0])
    if len(table_lines) < 14:
        return {}

    table_x0 = min(line[1] for line in table_lines)
    table_x1 = max(line[2] for line in table_lines)
    row_bounds = [(top[0], bottom[0]) for top, bottom in zip(table_lines[1:], table_lines[2:]) if bottom[0] > top[0] + 3]
    if len(row_bounds) < 12:
        return {}

    result: dict[tuple[int, int], fitz.Rect] = {}
    keys = [(1, number) for number in range(1, 8)]
    keys.extend((2, number) for number in range(1, 6))
    for index, key in enumerate(keys):
        top, bottom = row_bounds[index]
        result[key] = fitz.Rect(table_x0 - 1, max(0, top - 1), min(page.rect.width, table_x1 + 1), min(page.rect.height, bottom + 1))

    for offset, task_number in enumerate(range(8, 13), start=7):
        top, bottom = row_bounds[offset]
        result[(2, task_number)] = fitz.Rect(table_x0 - 1, max(0, top - 1), min(page.rect.width, table_x1 + 1), min(page.rect.height, bottom + 1))

    return result


def scanned_answer_row_pieces(
    document: fitz.Document,
    clip: fitz.Rect,
    directory: Path,
    prefix: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    page = document.load_page(0)
    image_path = directory / f"{prefix}-answer-p1.png"
    render_clip(page, clip, image_path)
    crop = {"x0": clip.x0, "y0": clip.y0, "x1": clip.x1, "y1": clip.y1}
    image = public_path(image_path)
    return [{"page": 1, "crop": crop, "image": image}], [image]


def starts_by_number(starts: list[Start]) -> dict[int, Start]:
    result: dict[int, Start] = {}
    for start in starts:
        result.setdefault(start.number, start)
    return result


def detect_part_heading_boundaries(document: fitz.Document) -> list[Start]:
    boundaries: list[Start] = []
    for page_index in range(document.page_count):
        page = document.load_page(page_index)
        page_dict = page.get_text("dict", sort=True)
        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                line_text = " ".join("".join(span.get("text", "") for span in line.get("spans", [])).split())
                if line_text.upper() != "II OSA":
                    continue
                x0, y0, _x1, _y1 = line["bbox"]
                boundaries.append(Start(number=0, page_index=page_index, x=float(x0), y=float(y0), heading=line_text, part=2))
    return boundaries


def task_key_for_answer(task_start: Start, part: int) -> tuple[int, int]:
    if task_start.part == 2 and task_start.number <= 5:
        return (2, task_start.number)
    if part == 2 and task_start.number >= 8:
        return (2, task_start.number)
    return (part, task_start.number)


def part_starts(starts: list[Start], part: int, combined: bool) -> list[Start]:
    if not combined:
        return starts
    if part == 1:
        filtered = [start for start in starts if start.part == 1 or (start.part is None and start.number <= 7)]
        return [start for start in filtered if start.number <= 7]
    filtered = [start for start in starts if start.part == 2 or start.number >= 8]
    return [start for start in filtered if start.number <= 5 or start.number >= 8]


def next_boundary_start(boundaries: list[Start], start: Start) -> Start | None:
    ordered = sorted(boundaries, key=lambda item: (item.page_index, item.y, item.number))
    for candidate in ordered:
        if (candidate.page_index, candidate.y) <= (start.page_index, start.y):
            continue
        return candidate
    return None


def extract_part(
    exam: dict[str, Any],
    part: int,
    grading_starts: dict[int, Start],
    answer_table_starts: dict[tuple[int, int], Start],
    scanned_answer_rows: dict[tuple[int, int], fitz.Rect],
    grading_doc: fitz.Document | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pdf_path_value = exam.get("part1Pdf" if part == 1 else "part2Pdf")
    year = int(exam["year"])
    source = str(exam.get("source") or "projektid")
    combined = bool(exam.get("combinedPdf")) or exam.get("part1Pdf") == exam.get("part2Pdf")
    combined_question_answer_tips = source == "kool" and "lahenduste ja kommentaaridega" in str(exam.get("formatNote") or "").lower()
    expected = 7 if part == 1 else 5
    report: dict[str, Any] = {
        "year": year,
        "source": source,
        "part": part,
        "detectedTaskCount": 0,
        "expectedTaskCount": expected,
        "missingTasks": [],
        "lowConfidenceTasks": [],
        "sourcePdfPath": pdf_path_value,
        "gradingPdfPath": exam.get("gradingPdf"),
        "gradingDocxPath": exam.get("gradingDocx"),
        "answerTablePdfPath": exam.get("answerTablePdf"),
    }
    if not pdf_path_value:
        report["missingTasks"] = list(range(1, expected + 1))
        return [], report

    source_pdf = STATIC / str(pdf_path_value).lstrip("/")
    if not source_pdf.exists():
        report["missingTasks"] = list(range(1, expected + 1))
        return [], report

    tasks: list[dict[str, Any]] = []
    with fitz.open(source_pdf) as document:
        all_starts = detect_starts(document)
        if not all_starts and source in {"arhmus", "kool"}:
            all_starts = detect_starts(document, allow_number_only=True)
        boundary_starts = [*all_starts, *detect_part_heading_boundaries(document)]
        starts = part_starts(all_starts, part, combined)
        report["detectedTaskCount"] = len(starts)
        detected_numbers = {start.number for start in starts}
        if starts:
            first_number = min(detected_numbers)
            expected_numbers = list(range(first_number, first_number + expected))
        else:
            expected_numbers = list(range(1, expected + 1))
        report["missingTasks"] = [number for number in expected_numbers if number not in detected_numbers]

        for index, start in enumerate(starts):
            next_start = starts[index + 1] if index + 1 < len(starts) else next_boundary_start(boundary_starts, start)
            task_id = f"{year}-{'i' if part == 1 else 'ii'}-{start.number}"
            task_pieces, task_images = crop_pieces(
                document,
                start,
                next_start,
                TASK_DIR,
                task_id,
                boundary_padding=55 if source == "kool" else 0,
            )

            answer_pieces: list[dict[str, Any]] = []
            answer_images: list[str] = []
            confidence = "high"
            needs_review = False
            answer_key = task_key_for_answer(start, part)
            answer_start = answer_table_starts.get(answer_key) or grading_starts.get(start.number)
            if grading_doc is not None and answer_key in scanned_answer_rows:
                answer_pieces, answer_images = scanned_answer_row_pieces(grading_doc, scanned_answer_rows[answer_key], ANSWER_DIR, task_id)
            elif grading_doc is not None and answer_start is not None:
                if answer_key in answer_table_starts:
                    ordered_answers = sorted(answer_table_starts.values(), key=lambda item: (item.page_index, item.y, item.part or 0, item.number))
                    answer_index = ordered_answers.index(answer_start)
                    answer_next = ordered_answers[answer_index + 1] if answer_index + 1 < len(ordered_answers) else None
                    answer_pieces, answer_images = answer_table_pieces(grading_doc, answer_start, answer_next, ANSWER_DIR, task_id)
                else:
                    ordered_answers = sorted(grading_starts.values(), key=lambda item: (item.page_index, item.y))
                    answer_index = ordered_answers.index(answer_start)
                    answer_next = ordered_answers[answer_index + 1] if answer_index + 1 < len(ordered_answers) else None
                    answer_pieces, answer_images = answer_page_pieces(grading_doc, answer_start, answer_next, ANSWER_DIR, task_id)
            else:
                confidence = "medium"
                needs_review = True

            if len(starts) != expected:
                confidence = "medium" if confidence == "high" else confidence
                needs_review = True
            if not answer_images:
                needs_review = True

            if needs_review:
                report["lowConfidenceTasks"].append(start.number)

            tasks.append(
                {
                    "id": task_id,
                    "year": year,
                    "source": source,
                    "part": part,
                    "taskNumber": start.number,
                    "title": f"{year} part {part} task {start.number}"
                    + (" (question + answer and tips)" if combined_question_answer_tips else ""),
                    "sourcePdf": str(pdf_path_value),
                    "gradingPdf": str(exam.get("gradingPdf") or exam.get("answerTablePdf") or ""),
                    "taskPieces": task_pieces,
                    "answerPieces": answer_pieces,
                    "taskImagePaths": task_images,
                    "answerImagePaths": answer_images,
                    "extractionConfidence": confidence,
                    "needsReview": needs_review,
                }
            )

    return tasks, report


def write_preview(tasks: list[dict[str, Any]]) -> None:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for task in tasks:
        first = task["taskImagePaths"][0] if task["taskImagePaths"] else ""
        review_label = "might be buggy" if int(task["year"]) < 2014 else "needs review"
        rows.append(f"<li>{task['id']} {review_label if task['needsReview'] else ''}<br><img src='../../{first.lstrip('/')}' width='400'></li>")
    html = "<!doctype html><meta charset='utf-8'><title>Extraction review</title><ul>" + "\n".join(rows) + "</ul>"
    (PREVIEW_DIR / "review.html").write_text(html, encoding="utf-8")


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    ANSWER_DIR.mkdir(parents=True, exist_ok=True)

    exams = load_exams()
    all_tasks: list[dict[str, Any]] = []
    report: list[dict[str, Any]] = []

    for exam in exams:
        grading_doc = None
        grading_starts: dict[int, Start] = {}
        answer_table_starts: dict[tuple[int, int], Start] = {}
        answer_row_crops: dict[tuple[int, int], fitz.Rect] = {}
        grading_pdf = exam.get("gradingPdf") or exam.get("answerTablePdf")
        if grading_pdf:
            grading_path = STATIC / str(grading_pdf).lstrip("/")
            if grading_path.exists():
                grading_doc = fitz.open(grading_path)
                grading_starts = starts_by_number(detect_starts(grading_doc))
                answer_table_starts = detect_answer_table_starts(grading_doc)
                answer_row_crops = detect_drawn_answer_rows(grading_doc) or detect_scanned_answer_rows(grading_doc)

        try:
            for part in (1, 2):
                tasks, part_report = extract_part(exam, part, grading_starts, answer_table_starts, answer_row_crops, grading_doc)
                all_tasks.extend(tasks)
                report.append(part_report)
        finally:
            if grading_doc is not None:
                grading_doc.close()

    all_tasks.sort(key=lambda task: (task["year"], task["part"], task["taskNumber"]))
    (DATA_DIR / "tasks.json").write_text(json.dumps(all_tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "extraction-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_preview(all_tasks)
    print(f"wrote {len(all_tasks)} tasks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
