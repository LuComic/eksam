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
    starts_by_key: dict[tuple[int, int], Start] = {}
    for page_index in range(document.page_count):
        page = document.load_page(page_index)
        blocks = page.get_text("blocks", sort=True)
        for block in blocks:
            if len(block) < 5:
                continue
            x0, y0, _x1, _y1, text = block[:5]
            block_text = " ".join(str(text).split())
            number = find_task_number(block_text, allow_number_only)
            if number is None:
                continue
            if block_text.startswith("Hindaja Ülesanne") and page.rect.width > 800:
                x0 = page.rect.width / 2 + 47
            if x0 > page.rect.width * 0.75:
                continue
            key = (page_index, number)
            start = Start(number=number, page_index=page_index, x=float(x0), y=float(y0), heading=block_text[:120])
            current = starts_by_key.get(key)
            if current is None or start.y < current.y:
                starts_by_key[key] = start
    ordered = sorted(starts_by_key.values(), key=lambda item: (item.page_index, item.y, item.number))
    by_number: dict[int, Start] = {}
    for start in ordered:
        by_number.setdefault(start.number, start)
    return sorted(by_number.values(), key=lambda item: item.number)


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
    top = min(max(0, y0 - 20), max(0, rect.height - 2))
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
            y0 = start.y
        else:
            y0 = 0

        boundary_on_page = None
        if effective_next and page_index == effective_next.page_index:
            if page_index != start.page_index or same_column(page, start, effective_next):
                boundary_on_page = effective_next

        if boundary_on_page and page_index == boundary_on_page.page_index:
            y1 = boundary_on_page.y
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


def starts_by_number(starts: list[Start]) -> dict[int, Start]:
    result: dict[int, Start] = {}
    for start in starts:
        result.setdefault(start.number, start)
    return result


def extract_part(exam: dict[str, Any], part: int, grading_starts: dict[int, Start], grading_doc: fitz.Document | None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pdf_path_value = exam.get("part1Pdf" if part == 1 else "part2Pdf")
    year = int(exam["year"])
    expected = 7 if part == 1 else 5
    report: dict[str, Any] = {
        "year": year,
        "part": part,
        "detectedTaskCount": 0,
        "expectedTaskCount": expected,
        "missingTasks": [],
        "lowConfidenceTasks": [],
        "sourcePdfPath": pdf_path_value,
        "gradingPdfPath": exam.get("gradingPdf"),
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
        starts = detect_starts(document)
        report["detectedTaskCount"] = len(starts)
        detected_numbers = {start.number for start in starts}
        if starts:
            first_number = min(detected_numbers)
            expected_numbers = list(range(first_number, first_number + expected))
        else:
            expected_numbers = list(range(1, expected + 1))
        report["missingTasks"] = [number for number in expected_numbers if number not in detected_numbers]

        for index, start in enumerate(starts):
            next_start = starts[index + 1] if index + 1 < len(starts) else None
            task_id = f"{year}-{'i' if part == 1 else 'ii'}-{start.number}"
            task_pieces, task_images = crop_pieces(document, start, next_start, TASK_DIR, task_id)

            answer_pieces: list[dict[str, Any]] = []
            answer_images: list[str] = []
            confidence = "high"
            needs_review = False
            answer_start = grading_starts.get(start.number)
            if grading_doc is not None and answer_start is not None:
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
                    "part": part,
                    "taskNumber": start.number,
                    "title": f"{year} part {part} task {start.number}",
                    "sourcePdf": str(pdf_path_value),
                    "gradingPdf": str(exam.get("gradingPdf") or ""),
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
        rows.append(f"<li>{task['id']} {'needs review' if task['needsReview'] else ''}<br><img src='../../{first.lstrip('/')}' width='400'></li>")
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
        grading_pdf = exam.get("gradingPdf")
        if grading_pdf:
            grading_path = STATIC / str(grading_pdf).lstrip("/")
            if grading_path.exists():
                grading_doc = fitz.open(grading_path)
                grading_starts = starts_by_number(detect_starts(grading_doc))

        try:
            for part in (1, 2):
                tasks, part_report = extract_part(exam, part, grading_starts, grading_doc)
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
