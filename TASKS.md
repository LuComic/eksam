
You are working on an existing SvelteKit + Bun project for studying Estonian “laia kursuse” mathematics state exam tasks.

The site already exists. Do not rebuild it from scratch.

Your task is to add support for older exam materials from 2014–2020.

Current state:
- The app already supports newer exam materials, currently focused around 2021–2025.
- The app already has a pipeline for fetching PDFs, extracting/cropping tasks, generating JSON, and rendering tasks in the UI.
- The app already uses SvelteKit, Bun, Python, and PyMuPDF.
- Preserve the existing UI and architecture unless a small change is required for this feature.

Feature goal:
Add older “laia kursuse” mathematics state exam materials from 2014–2020 using TLÜ Eesti Pedagoogika Arhiivmuuseum / arhmus.tlu.ee as an additional source.

Important:
- This is an addition to the existing project, not a rewrite.
- Keep the UI simple.
- Do not add a database.
- Do not add login.
- Do not add mobile optimization.
- Do not add fake tasks.
- Do not break existing 2021–2025 support.
- Continue using Bun commands for the JS/SvelteKit side.
- Continue using Python + PyMuPDF for PDF extraction.

Background:
The newer Harno/projektid source only covers the newer years well. Older PDFs are available through arhmus.tlu.ee, often as direct PDF files under URLs like:

https://arhmus.tlu.ee/tlibrary/f/text/42/Laia_kursuse_hindamisjuhend_RE_matemaatika_2019_117742.pdf
https://arhmus.tlu.ee/tlibrary/f/text/24/Laia_kursuse_eksamit_I_osa_RE_matemaatika_2018_115224.pdf
https://arhmus.tlu.ee/tlibrary/f/text/65/Lisa_7_mat_RE_2017_lai_I_osa_eesti_113365.pdf
https://arhmus.tlu.ee/tlibrary/f/text/65/Lisa_8_mat_RE_2017_lai_II_osa_eesti_113365.pdf

The arhmus source is less clean than projektid. Do not assume it has the same yearly Confluence-style page structure.

Implementation requirements:

1. Add a second source type

The project should support at least these source types:

- projektid
  - Used for 2021–2025.
  - Existing behavior should keep working.

- arhmus
  - Used for 2014–2020.
  - Should support manually configured direct PDF URLs per year.
  - Can later be improved with discovery/search, but direct URL config is enough for now.

Add source metadata to generated data where useful:

type ExamSource = 'projektid' | 'arhmus';

Existing Exam/Task objects should include source information if they do not already:

source: 'projektid' | 'arhmus';

2. Add manually configurable older-year PDF mappings

Create or update a config file for source materials, for example:

scripts/sources.py

or, if the existing project already has a config file, extend that instead.

The config should allow entries like:

{
  "year": 2019,
  "source": "arhmus",
  "part1PdfUrl": "...",
  "part2PdfUrl": "...",
  "gradingPdfUrl": "...",
  "answerTablePdfUrl": "..."
}

Not every year may have every URL at first. The pipeline should handle partial data gracefully.

3. Add known arhmus URLs

Start with the known URLs already found in research:

2019:
- grading guide:
  https://arhmus.tlu.ee/tlibrary/f/text/42/Laia_kursuse_hindamisjuhend_RE_matemaatika_2019_117742.pdf

2018:
- I osa:
  https://arhmus.tlu.ee/tlibrary/f/text/24/Laia_kursuse_eksamit_I_osa_RE_matemaatika_2018_115224.pdf
- vastavustabel / answer table:
  https://arhmus.tlu.ee/tlibrary/f/text/24/Laia_kursuse_vastavustabel_RE_matemaatika_2018_115224.pdf

2017:
- I osa:
  https://arhmus.tlu.ee/tlibrary/f/text/65/Lisa_7_mat_RE_2017_lai_I_osa_eesti_113365.pdf
- II osa:
  https://arhmus.tlu.ee/tlibrary/f/text/65/Lisa_8_mat_RE_2017_lai_II_osa_eesti_113365.pdf

Also search the existing source archive for 2014, 2015, 2016, 2018 II osa, 2019 I osa, 2019 II osa, 2020 I osa, 2020 II osa, and matching grading/answer PDFs. Add any reliable direct arhmus PDF URLs you find to the config.

Use only reliable direct PDF URLs. Avoid Scribd or other random reuploads as primary sources.

4. Download behavior

Extend the fetch pipeline so it can download both:
- projektid PDFs from existing page scraping
- arhmus PDFs from manually configured direct URLs

Downloaded files should still go into the existing local PDF directory, for example:

static/pdfs/

Use normalized filenames, for example:

2018-laia-i.pdf
2018-laia-ii.pdf
2018-hindamisjuhend.pdf
2018-vastavustabel.pdf

Do not duplicate downloads unnecessarily if the file already exists and looks valid.

5. Extraction behavior

Run the existing extraction/cropping logic on arhmus PDFs too.

The older PDFs may have slightly different heading formats, so make the task-start detection tolerant.

Support these heading patterns:

- Ülesanne 1
- Ülesanne 1.
- Ylesanne 1
- 1.
- Lisa-style PDFs where task text may start after cover/instruction pages

If detection is uncertain:
- still create a fallback page-level crop if possible,
- mark needsReview: true,
- set extractionConfidence to medium or low,
- add details to extraction-report.json.

Do not OCR unless the PDF has no text layer. If OCR would be needed, mark the file as needsReview instead.

6. Answer/grading matching

Older years may have:
- hindamisjuhend PDFs,
- vastavustabel PDFs,
- both,
- or only partial answer material.

Use the best available answer source in this order:
1. hindamisjuhend
2. vastavustabel
3. no answer source, mark answer missing

If answers cannot be matched per task, still include the task and mark answerPieces as empty or needsReview.

The UI should not crash if a task has no answer image.

7. UI behavior

Preserve the current UI.

The only expected UI change is that year selectors and random/shuffle modes should include the newly available older years once the pipeline generates them.

For example:
- single task mode can now randomly include 2014–2020 tasks.
- exam mode year select can include 2014–2025 if data exists.
- shuffle exam mode can mix 2014–2025 tasks.

If a year has incomplete data, still show it if tasks exist, but avoid crashing when answers are missing.

If useful, display a small “needs review” label for low-confidence extracted tasks, consistent with current behavior.

8. Pipeline commands

Keep using Bun commands:

bun run fetch
bun run extract
bun run pipeline
bun run dev
bun run build

Do not replace Bun with npm/yarn/pnpm.

Python dependencies should remain in requirements.txt.

9. Data/reporting requirements

Update or preserve:

static/data/exams.json
static/data/tasks.json
static/data/extraction-report.json

The extraction report should include source information:

{
  "year": 2018,
  "source": "arhmus",
  "part": 1,
  "detectedTaskCount": 7,
  "expectedTaskCount": 7,
  "missingTasks": [],
  "lowConfidenceTasks": [],
  "sourcePdf": "/pdfs/2018-laia-i.pdf",
  "gradingPdf": "/pdfs/2018-hindamisjuhend.pdf"
}

10. Acceptance criteria

The feature is complete when:

- Existing 2021–2025 projektid support still works.
- The pipeline supports arhmus direct PDF sources.
- At least some older years from 2014–2020 can be downloaded and processed.
- 2017 and 2018 laia I/II or answer-related files are included where direct URLs are available.
- Generated tasks from older years appear in the same UI as newer tasks.
- Single task mode can show older tasks.
- Exam mode can show older years when extracted data exists.
- Shuffle exam mode can include older tasks.
- Missing answers do not crash the UI.
- extraction-report.json clearly marks incomplete or uncertain older-year data.
- bun run pipeline completes without breaking the project.
- bun run build succeeds.

Implementation style:
Make the smallest changes necessary.
Follow the current project structure.
Do not rewrite existing working code unless required.
Keep the implementation simple and understandable.
