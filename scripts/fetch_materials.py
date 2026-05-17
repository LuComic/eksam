from __future__ import annotations

import html
import json
import re
import ssl
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.parse import parse_qs, quote, unquote, urljoin, urlparse
from urllib.request import Request, urlopen

from sources import (
    ARHMUS_MATERIALS,
    KOOL_MATERIALS,
    LOCAL_NEW_EXAM_YEARS,
    PROJEKTID_YEAR_PAGES,
)

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
PDF_DIR = STATIC / "pdfs"
DATA_DIR = STATIC / "data"

USER_AGENT = "Mozilla/5.0 exam-shuffler/0.1"


@dataclass(frozen=True)
class PdfCandidate:
    year: int
    kind: str
    filename: str
    url: str
    local_path: str
    source: str = "projektid"


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=60) as response:
            return response.read()
    except URLError as exc:
        if "CERTIFICATE_VERIFY_FAILED" not in str(exc):
            raise
        context = ssl._create_unverified_context()
        with urlopen(request, timeout=60, context=context) as response:
            return response.read()


def extract_pdf_urls(page_url: str, body: str) -> list[str]:
    urls: set[str] = set()
    unescaped = html.unescape(body)

    for match in re.finditer(
        r"""(?:href|src)=["']([^"']+\.pdf[^"']*)["']""", unescaped, re.I
    ):
        urls.add(urljoin(page_url, match.group(1)))

    for match in re.finditer(r"""preview=(/[^"'<>\s]+?\.pdf)""", unescaped, re.I):
        urls.add(f"{page_url}?preview={match.group(1)}")

    for match in re.finditer(
        r"""/download/attachments/\d+/[^"'<>\s]+?\.pdf(?:\?[^"'<>\s]+)?""",
        unescaped,
        re.I,
    ):
        urls.add(urljoin(page_url, match.group(0)))

    return sorted(urls)


def attachment_download_url(url: str) -> tuple[str, str] | None:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    preview = query.get("preview", [None])[0]
    if preview:
        parts = preview.strip("/").split("/", 2)
        if len(parts) == 3:
            page_id, _attachment_id, filename = parts
            return (
                f"https://projektid.edu.ee/download/attachments/{page_id}/{quote(unquote(filename))}?api=v2",
                unquote(filename),
            )

    if "/download/attachments/" in parsed.path and parsed.path.lower().endswith(".pdf"):
        return (url, unquote(Path(parsed.path).name))

    return None


def classify_pdf(filename: str) -> str | None:
    lowered = filename.casefold()
    normalized = re.sub(r"[_\-\s]+", " ", lowered)
    if "matemaatika" not in lowered or "laia" not in lowered:
        return None
    if "vene" in lowered or "ukraina" in lowered or "kitsas" in lowered:
        return None
    if (
        "hindamisjuhend" in lowered
        or "hindamine" in lowered
        or "vastavustabel" in lowered
    ):
        return "grading"
    if re.search(r"\bi\s*osa\b", normalized) and not re.search(
        r"\bii\s*osa\b", normalized
    ):
        return "part1"
    if re.search(r"\bii\s*osa\b", normalized):
        return "part2"
    return None


def local_pdf_name(year: int, kind: str) -> str:
    suffix = {
        "combined": "laia",
        "part1": "laia-i",
        "part2": "laia-ii",
        "grading": "hindamisjuhend",
        "answerTable": "vastavustabel",
    }[kind]
    return f"{year}-{suffix}.pdf"


def local_document_name(year: int, kind: str, extension: str) -> str:
    suffix = {"gradingDocx": "hindamisjuhend"}[kind]
    return f"{year}-{suffix}.{extension}"


def candidate_score(year: int, kind: str, filename: str) -> int:
    lowered = filename.casefold()
    if kind == "grading":
        if year == 2021 and "vastavustabel" in lowered:
            return 4
        if year != 2021 and "hindamisjuhend" in lowered:
            return 4
        if "vastavustabel" in lowered:
            return 2
        if "hindamisjuhend" in lowered:
            return 1
    if "eesti keeles" in lowered:
        return 3
    if "vene" not in lowered and "ukraina" not in lowered:
        return 2
    return 1


def find_candidates(year: int, page_url: str) -> list[PdfCandidate]:
    body = fetch_bytes(page_url).decode("utf-8", errors="replace")
    candidates: dict[str, PdfCandidate] = {}
    for found_url in extract_pdf_urls(page_url, body):
        normalized = attachment_download_url(found_url)
        if normalized is None:
            continue
        download_url, filename = normalized
        kind = classify_pdf(filename)
        if kind is None:
            continue
        local_path = f"/pdfs/{local_pdf_name(year, kind)}"
        current = candidates.get(kind)
        if current is None or candidate_score(year, kind, filename) > candidate_score(
            year, kind, current.filename
        ):
            candidates[kind] = PdfCandidate(
                year, kind, filename, download_url, local_path, "projektid"
            )
    return list(candidates.values())


def direct_source_candidates(
    materials: list[dict[str, object]], source: str
) -> dict[int, list[PdfCandidate]]:
    key_to_kind = {
        "combinedPdfUrl": "combined",
        "part1PdfUrl": "part1",
        "part2PdfUrl": "part2",
        "gradingPdfUrl": "grading",
        "answerTablePdfUrl": "answerTable",
        "gradingDocxUrl": "gradingDocx",
    }
    candidates_by_year: dict[int, list[PdfCandidate]] = {}
    for material in materials:
        year = int(material["year"])
        candidates: list[PdfCandidate] = []
        for key, kind in key_to_kind.items():
            url = material.get(key)
            if not url:
                continue
            filename = unquote(Path(urlparse(str(url)).path).name)
            if kind == "gradingDocx":
                candidates.append(
                    PdfCandidate(
                        year,
                        kind,
                        filename,
                        str(url),
                        f"/pdfs/{local_document_name(year, kind, 'docx')}",
                        source,
                    )
                )
            else:
                candidates.append(
                    PdfCandidate(
                        year,
                        kind,
                        filename,
                        str(url),
                        f"/pdfs/{local_pdf_name(year, kind)}",
                        source,
                    )
                )
        candidates_by_year[year] = candidates
    return candidates_by_year


def local_new_exam_candidates() -> dict[int, list[PdfCandidate]]:
    candidates_by_year: dict[int, list[PdfCandidate]] = {}
    for year in LOCAL_NEW_EXAM_YEARS:
        exam_pdf = PDF_DIR / local_pdf_name(year, "combined")
        answer_pdf = PDF_DIR / local_pdf_name(year, "grading")
        candidates: list[PdfCandidate] = []
        if exam_pdf.exists():
            candidates.append(
                PdfCandidate(
                    year,
                    "combined",
                    exam_pdf.name,
                    exam_pdf.resolve().as_uri(),
                    f"/pdfs/{local_pdf_name(year, 'combined')}",
                    "local_new_exams",
                )
            )
        if answer_pdf.exists():
            candidates.append(
                PdfCandidate(
                    year,
                    "grading",
                    answer_pdf.name,
                    answer_pdf.resolve().as_uri(),
                    f"/pdfs/{local_pdf_name(year, 'grading')}",
                    "local_new_exams",
                )
            )
        if candidates:
            candidates_by_year[year] = candidates
    return candidates_by_year


def is_valid_pdf(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 1024:
        return False
    with path.open("rb") as handle:
        return handle.read(5) == b"%PDF-"


def is_valid_download(path: Path) -> bool:
    if path.suffix.casefold() == ".pdf":
        return is_valid_pdf(path)
    return path.exists() and path.stat().st_size >= 1024


def download(candidates: Iterable[PdfCandidate]) -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    for candidate in candidates:
        target = PDF_DIR / Path(candidate.local_path).name
        parsed = urlparse(candidate.url)
        if parsed.scheme == "file":
            source = Path(unquote(parsed.path))
            if not source.exists():
                print(f"missing local {candidate.year} {candidate.kind}: {source}")
                continue
            if (
                not is_valid_download(target)
                or target.read_bytes() != source.read_bytes()
            ):
                print(
                    f"copying {candidate.year} {candidate.kind}: {candidate.filename}"
                )
                target.write_bytes(source.read_bytes())
            else:
                print(
                    f"skipping {candidate.year} {candidate.kind}: {target.name} already exists"
                )
            continue

        if is_valid_download(target):
            print(
                f"skipping {candidate.year} {candidate.kind}: {target.name} already exists"
            )
            continue
        print(f"downloading {candidate.year} {candidate.kind}: {candidate.filename}")
        target.write_bytes(fetch_bytes(candidate.url))


def build_exams(
    candidates_by_year: dict[int, list[PdfCandidate]],
) -> list[dict[str, object]]:
    exams: list[dict[str, object]] = []
    for material in [*KOOL_MATERIALS, *ARHMUS_MATERIALS]:
        year = int(material["year"])
        by_kind = {
            candidate.kind: candidate.local_path
            for candidate in candidates_by_year.get(year, [])
        }
        exams.append(
            {
                "year": year,
                "source": material.get("source", "arhmus"),
                "combinedPdf": by_kind.get("combined"),
                "part1Pdf": by_kind.get("part1") or by_kind.get("combined"),
                "part2Pdf": by_kind.get("part2") or by_kind.get("combined"),
                "gradingPdf": by_kind.get("grading"),
                "gradingDocx": by_kind.get("gradingDocx"),
                "answerTablePdf": by_kind.get("answerTable"),
                "formatNote": material.get("formatNote"),
                "sourcePageUrl": material.get(
                    "sourcePageUrl", "https://arhmus.tlu.ee/"
                ),
            }
        )

    for year in LOCAL_NEW_EXAM_YEARS:
        by_kind = {
            candidate.kind: candidate.local_path
            for candidate in candidates_by_year.get(year, [])
        }
        if not by_kind:
            continue
        exams.append(
            {
                "year": year,
                "source": "local_new_exams",
                "combinedPdf": by_kind.get("combined"),
                "part1Pdf": by_kind.get("combined"),
                "part2Pdf": by_kind.get("combined"),
                "gradingPdf": by_kind.get("grading"),
                "sourcePageUrl": "/pdfs/",
                "formatNote": "local combined exam PDF with answer table",
            }
        )

    for year, page_url in PROJEKTID_YEAR_PAGES.items():
        by_kind = {
            candidate.kind: candidate.local_path
            for candidate in candidates_by_year.get(year, [])
        }
        exams.append(
            {
                "year": year,
                "source": "projektid",
                "part1Pdf": by_kind.get("part1"),
                "part2Pdf": by_kind.get("part2"),
                "gradingPdf": by_kind.get("grading"),
                "sourcePageUrl": page_url,
            }
        )
    return exams


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    candidates_by_year = direct_source_candidates(KOOL_MATERIALS, "kool")
    for year, candidates in candidates_by_year.items():
        print(f"configured kool {year}")
        for candidate in candidates:
            print(f"  {candidate.kind}: {candidate.filename}")
        download(candidates)

    arhmus_by_year = direct_source_candidates(ARHMUS_MATERIALS, "arhmus")
    candidates_by_year.update(arhmus_by_year)
    for year, candidates in arhmus_by_year.items():
        print(f"configured arhmus {year}")
        for candidate in candidates:
            print(f"  {candidate.kind}: {candidate.filename}")
        download(candidates)

    local_by_year = local_new_exam_candidates()
    candidates_by_year.update(local_by_year)
    for year, candidates in local_by_year.items():
        print(f"configured local_new_exams {year}")
        for candidate in candidates:
            print(f"  {candidate.kind}: {candidate.filename}")
        download(candidates)

    for year, page_url in PROJEKTID_YEAR_PAGES.items():
        print(f"fetching {year}")
        candidates = find_candidates(year, page_url)
        candidates_by_year[year] = candidates
        for candidate in candidates:
            print(f"  {candidate.kind}: {candidate.filename}")
        download(candidates)

    exams = build_exams(candidates_by_year)
    (DATA_DIR / "exams.json").write_text(
        json.dumps(exams, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
