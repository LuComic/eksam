# Estonian Math Exam Shuffler

Private SvelteKit study site for practicing Estonian wide-course mathematics state exam tasks from 2014-2025.

The app uses real local data only. It downloads PDFs from `projektid.edu.ee` and `arhmus.tlu.ee`, extracts task and grading regions with PyMuPDF, writes JSON under `static/data/`, and renders PNG crops in the browser.

## Install

Install Bun from <https://bun.sh/docs/installation>.

Install JavaScript dependencies:

```bash
bun install
```

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Data Pipeline

Fetch the year pages, download matching PDFs, and generate `static/data/exams.json`:

```bash
bun run fetch
```

Extract task and answer crops from downloaded PDFs and generate `static/data/tasks.json` plus `static/data/extraction-report.json`:

```bash
bun run extract
```

Run the full pipeline:

```bash
bun run pipeline
```

Generated files are written to:

- `static/pdfs/`
- `static/generated/tasks/`
- `static/generated/answers/`
- `static/generated/previews/review.html`
- `static/data/exams.json`
- `static/data/tasks.json`
- `static/data/extraction-report.json`

## Run The App

Start the dev server:

```bash
bun run dev
```

Build the static site:

```bash
bun run build
```

Preview the production build:

```bash
bun run preview
```

## Adding A New Year

Add newer `projektid.edu.ee` year pages to `PROJEKTID_YEAR_PAGES` in `scripts/sources.py`.

Add older direct `arhmus.tlu.ee` PDF URLs to `ARHMUS_MATERIALS` in `scripts/sources.py`. Entries can be partial; use `part1PdfUrl`, `part2PdfUrl`, `gradingPdfUrl`, and `answerTablePdfUrl` as available.

Then run:

```bash
bun run pipeline
```

The fetch script extracts `projektid.edu.ee` PDF links from page HTML and handles both Confluence preview URLs and direct `/download/attachments/...` URLs. `arhmus.tlu.ee` materials are downloaded from the direct PDF URLs configured in `scripts/sources.py`.

## Fixing Extraction

If a crop is wrong, first inspect:

- `static/data/extraction-report.json`
- `static/generated/previews/review.html`
- `static/generated/tasks/`
- `static/generated/answers/`

The extractor logic lives in `scripts/extract_tasks.py`. Boundary detection is based on PDF text blocks and task heading regexes. If a specific PDF needs adjustment, update the detection/cropping rules there, then rerun:

```bash
bun run extract
```

Do not add fake task data to `tasks.json`; the UI is intentionally empty until real extracted data exists.
# eksam
