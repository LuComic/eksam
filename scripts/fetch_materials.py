from __future__ import annotations

import html
import json
import re
import ssl
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, quote, unquote, urljoin, urlparse
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
PDF_DIR = STATIC / "pdfs"
DATA_DIR = STATIC / "data"

YEAR_PAGES = {
    2021: "https://projektid.edu.ee/spaces/THO/pages/322207772/Riigieksamite+materjalid+2021",
    2022: "https://projektid.edu.ee/spaces/THO/pages/313819017/Riigieksamite+materjalid+2022",
    2023: "https://projektid.edu.ee/spaces/THO/pages/313818909/Riigieksamite+materjalid+2023",
    2024: "https://projektid.edu.ee/spaces/THO/pages/313818006/Riigieksamite+materjalid+2024",
    2025: "https://projektid.edu.ee/spaces/THO/pages/313817358/Riigieksamite+materjalid+2025",
}

USER_AGENT = "Mozilla/5.0 exam-shuffler/0.1"


@dataclass(frozen=True)
class PdfCandidate:
    year: int
    kind: str
    filename: str
    url: str
    local_path: str


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

    for match in re.finditer(r"""(?:href|src)=["']([^"']+\.pdf[^"']*)["']""", unescaped, re.I):
        urls.add(urljoin(page_url, match.group(1)))

    for match in re.finditer(r"""preview=(/[^"'<>\s]+?\.pdf)""", unescaped, re.I):
        urls.add(f"{page_url}?preview={match.group(1)}")

    for match in re.finditer(r"""/download/attachments/\d+/[^"'<>\s]+?\.pdf(?:\?[^"'<>\s]+)?""", unescaped, re.I):
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
    if "hindamisjuhend" in lowered or "hindamine" in lowered or "vastavustabel" in lowered:
        return "grading"
    if re.search(r"\bi\s*osa\b", normalized) and not re.search(r"\bii\s*osa\b", normalized):
        return "part1"
    if re.search(r"\bii\s*osa\b", normalized):
        return "part2"
    return None


def local_pdf_name(year: int, kind: str) -> str:
    suffix = {"part1": "laia-i", "part2": "laia-ii", "grading": "hindamisjuhend"}[kind]
    return f"{year}-{suffix}.pdf"


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
        if current is None or candidate_score(year, kind, filename) > candidate_score(year, kind, current.filename):
            candidates[kind] = PdfCandidate(year, kind, filename, download_url, local_path)
    return list(candidates.values())


def download(candidates: Iterable[PdfCandidate]) -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    for candidate in candidates:
        target = PDF_DIR / Path(candidate.local_path).name
        print(f"downloading {candidate.year} {candidate.kind}: {candidate.filename}")
        target.write_bytes(fetch_bytes(candidate.url))


def build_exams(candidates_by_year: dict[int, list[PdfCandidate]]) -> list[dict[str, object]]:
    exams: list[dict[str, object]] = []
    for year, page_url in YEAR_PAGES.items():
        by_kind = {candidate.kind: candidate.local_path for candidate in candidates_by_year.get(year, [])}
        exams.append(
            {
                "year": year,
                "part1Pdf": by_kind.get("part1"),
                "part2Pdf": by_kind.get("part2"),
                "gradingPdf": by_kind.get("grading"),
                "sourcePageUrl": page_url,
            }
        )
    return exams


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    candidates_by_year: dict[int, list[PdfCandidate]] = {}
    for year, page_url in YEAR_PAGES.items():
        print(f"fetching {year}")
        candidates = find_candidates(year, page_url)
        candidates_by_year[year] = candidates
        for candidate in candidates:
            print(f"  {candidate.kind}: {candidate.filename}")
        download(candidates)

    exams = build_exams(candidates_by_year)
    (DATA_DIR / "exams.json").write_text(json.dumps(exams, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
