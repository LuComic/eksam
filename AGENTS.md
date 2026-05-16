You are building a simple private study website for Estonian mathematics state exam practice.

The user will not code this manually. Implement the whole project.

High-level goal:
Create a SvelteKit website where students can study previous Estonian “laia kursuse” mathematics state exam tasks from 2021–2025. The app should fetch/download PDFs from projektid.edu.ee, extract individual task regions, and let users view either a single random task, a full exam by year, or a shuffled exam made from tasks across years.

This is not a polished production product. Prioritize making the full pipeline work:
1. Fetch/download PDFs.
2. Detect/crop tasks and answer/grading regions.
3. Generate structured JSON.
4. Render the app simply in SvelteKit.
5. Keep UI default and plain.

Tech requirements:
- Use SvelteKit.
- Use TypeScript for the SvelteKit app.
- Use Bun as the JavaScript runtime, package manager, and script runner.
- Use Bun commands everywhere for the JavaScript/SvelteKit side.
- Do not use npm, pnpm, or yarn commands in README instructions or package scripts unless explicitly mentioning them as alternatives.
- Use Python for PDF extraction.
- Use PyMuPDF / fitz for PDF parsing, text block coordinate detection, and rendering cropped task images.
- Use local static files for PDFs and generated task/answer images.
- Prefer a static SvelteKit app with adapter-static unless a backend endpoint is absolutely necessary.
- Do not optimize for mobile. Desktop only.
- Do not build fancy styling. Use plain default HTML/CSS.

Known source pages:
The source is projektid.edu.ee.

Known year pages:
- 2021 page:
  https://projektid.edu.ee/spaces/THO/pages/322207772/Riigieksamite+materjalid+2021
- 2022 page:
  https://projektid.edu.ee/spaces/THO/pages/313819017/Riigieksamite+materjalid+2022
- 2023 page:
  https://projektid.edu.ee/spaces/THO/pages/313818909/Riigieksamite+materjalid+2023
- 2024 page:
  https://projektid.edu.ee/spaces/THO/pages/313818006/Riigieksamite+materjalid+2024
- 2025 page:
  https://projektid.edu.ee/spaces/THO/pages/313817358/Riigieksamite+materjalid+2025
- 2026 page exists but is currently not useful for practice.

Known direct/example 2025 URLs:
- 2025 laia math II osa tasks:
  https://projektid.edu.ee/spaces/THO/pages/313817358/Riigieksamite+materjalid+2025?preview=/313817358/313817984/Laia%20kursuse%20eksamit%C3%B6%C3%B6%20eesti%20keeles%20II%20osa%20(RE%20matemaatika%202025).pdf
- 2025 laia math I osa tasks:
  https://projektid.edu.ee/spaces/THO/pages/313817358/Riigieksamite+materjalid+2025?preview=/313817358/313817983/Laia%20kursuse%20eksamitöö%20eesti%20keeles%20I%20osa%20(RE%20matemaatika%202025).pdf
- 2025 laia math grading/solutions:
  https://projektid.edu.ee/spaces/THO/pages/313817358/Riigieksamite+materjalid+2025?preview=/313817358/313817981/Laia%20kursuse%20eksami%20hindamisjuhend%20(RE%20matemaatika%202025).pdf
- 2021 laia math II osa:
  https://projektid.edu.ee/spaces/THO/pages/322207772/Riigieksamite+materjalid+2021?preview=/322207772/322207909/Laia%20kursuse%20eksamitöö%20II%20osa%20(RE%20matemaatika%202021).pdf

Important source behavior:
- Do not hardcode attachment IDs only.
- Write a fetch script that loads each year page and extracts PDF links from the HTML.
- Handle both URL forms:
  1. Preview URLs:
     /spaces/THO/pages/{pageId}/...?preview=/{pageId}/{attachmentId}/{filename}.pdf
  2. Direct download URLs:
     /download/attachments/{pageId}/{filename}.pdf?api=v2
- Store downloaded PDFs locally under static/pdfs/.
- Generate metadata under static/data/.

Only target “laia kursuse” mathematics, Estonian language, for now.
Ignore “kitsas” and Russian-language files for now unless needed later.

Expected project structure:
exam-shuffler/
  package.json
  bun.lock
  svelte.config.js
  vite.config.ts
  requirements.txt
  src/
    routes/
      +page.svelte
    lib/
      types.ts
      data.ts
      random.ts
      components/
        TaskViewer.svelte
        ExamViewer.svelte
        ShuffleExamViewer.svelte
        AnswerPane.svelte
  static/
    data/
      exams.json
      tasks.json
      extraction-report.json
    pdfs/
      2021-laia-i.pdf
      2021-laia-ii.pdf
      2021-hindamisjuhend.pdf
      ...
    generated/
      tasks/
        2025-i-1.png
        2025-i-2.png
        ...
      answers/
        2025-i-1.png
        2025-i-2.png
        ...
      previews/
        review.html or per-year preview images
  scripts/
    fetch_materials.py
    extract_tasks.py
    build_data.py
    run_pipeline.py
  README.md

Data model:
Create TypeScript types:

type Mode = 'single-task' | 'exam' | 'shuffle-exam';

type Exam = {
  year: number;
  part1Pdf?: string;
  part2Pdf?: string;
  gradingPdf?: string;
  sourcePageUrl: string;
};

type CropBox = {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
};

type PageCrop = {
  page: number;
  crop: CropBox | null;
  image?: string;
};

type Task = {
  id: string;
  year: number;
  part: 1 | 2;
  taskNumber: number;
  title: string;
  sourcePdf: string;
  gradingPdf: string;
  taskPieces: PageCrop[];
  answerPieces: PageCrop[];
  taskImagePaths: string[];
  answerImagePaths: string[];
  points?: number;
  extractionConfidence: 'high' | 'medium' | 'low';
  needsReview: boolean;
};

Fetching workflow:
1. For each known year page, download the HTML.
2. Extract all PDF URLs.
3. Normalize PDF names.
4. Keep PDFs that match:
   - laia
   - matemaatika
   - eesti keeles if present
   - I osa
   - II osa
   - hindamisjuhend
5. Download those PDFs into static/pdfs/.
6. Generate static/data/exams.json.

Extraction workflow:
1. Open each exam PDF with PyMuPDF.
2. Extract text blocks from each page using page.get_text("blocks", sort=True).
3. Detect task starts using robust regex patterns:
   - Ülesanne\s+(\d+)
   - Ylesanne\s+(\d+)
   - ^\s*(\d+)\.\s
   - Also tolerate “Ülesanne nr” if found.
4. Store detected task start:
   - task number
   - page number
   - y coordinate
   - detected heading text
5. Convert consecutive task starts into page/crop ranges:
   - If task A starts on same page before task B, crop from A.y to B.y.
   - If task spans pages, create multiple pieces:
     first page: A.y to bottom
     middle pages: full page
     last page: top to next task y
6. Add margins around crops:
   - x0: 30
   - y0: max(0, detectedY - 20)
   - x1: page width - 30
   - y1: nextY - 10 or page height - 30
7. Render each crop to PNG using PyMuPDF at a readable resolution, e.g. 2x scale.
8. Save images under static/generated/tasks/.
9. Repeat similar extraction for the grading/solutions PDF:
   - Detect “Ülesanne N” starts.
   - Crop grading/solution regions per task.
   - Save under static/generated/answers/.
10. If answer matching is uncertain, still include the likely answer pages/crops but mark needsReview: true.
11. Generate static/data/tasks.json.
12. Generate static/data/extraction-report.json with:
   - year
   - part
   - detected task count
   - expected task count
   - missing tasks
   - low-confidence tasks
   - source PDF path
   - grading PDF path

Important extraction behavior:
- Do not attempt to convert math tasks into HTML text.
- The user-facing task should be shown as the original cropped PDF rendering, i.e. PNG images generated from the PDF.
- Text extraction is only used to detect boundaries.
- Keep original PDFs available too.
- If crop detection fails for a task, fall back to showing the full page image and mark needsReview: true.
- Make the crop system tolerant; it is better to include too much page area than cut off part of a task.
- The UI should be implemented before the extractor is perfect, but it must use real generated data only. If the real extraction pipeline has not been run yet, show loading/empty states instead of fake tasks.
- Generated task crops must be PNG images created from the actual PDFs. Use PyMuPDF’s page rendering/cropping capability, e.g. rendering page clips to pixmaps/images. Do not manually invent placeholder images.

Expected task counts:
- Default full generated exam should contain 12 tasks.
- Assume part I usually has 7 tasks and part II usually has 5 tasks.
- Still detect actual counts from PDFs and do not crash if a year differs.
- For “shuffle exam”, generate 12 tasks total:
  - Prefer 7 tasks from part I and 5 from part II.
  - Mix years randomly.
  - Avoid duplicate exact tasks.
  - Keep selected tasks in stable order after generation, not reshuffling on every render.

SvelteKit UI requirements:
Initial page:
- Initially mostly blank.
- At the top, show a select with exactly these options:
  - empty/default option
  - single task
  - exam
  - shuffle exam
- Nothing else is shown until a mode is selected.

Global top controls after mode is selected:
- Keep the initial mode select visible at the top.
- Next to it, show a “show answer” checkbox or toggle.
- If show answer is false:
  - Show only the task/exam content.
- If show answer is true:
  - Split the page into two equal columns:
    - left: task/exam
    - right: grading/solutions div
  - Use CSS grid with two 50% columns.
  - Desktop only. No mobile optimization needed.

Loading and empty-state requirements:
- Do not use fake tasks.
- On first app load, try to load /data/tasks.json and /data/exams.json.
- While loading, show simple text:
  “Loading materials…”
- If JSON files are missing, invalid, or empty, show:
  “No extracted tasks found yet. Run bun run pipeline.”
- If extraction exists but some tasks are marked needsReview, still show them, but display a small “needs review” label.
- The app should not crash if data files are missing.
- Single task, exam, and shuffle exam modes should be disabled or show a clear empty message until real data exists.

Mode: single task
- Pick a random task from tasks.json on initial selection.
- Show the cropped task image(s).
- Somewhere close to the task, show previous and next controls.
- Previous/next should move through a shuffled task list.
- The order should be generated once per session so previous works.
- Show minimal metadata:
  - year
  - part
  - task number
- If show answer is true, show the matching cropped answer image(s) in the right pane.
- Add a “new random” button if useful, but keep UI plain.

Mode: exam
- After selecting exam mode, show a year select.
- The student chooses a year.
- Show the exam like an exam, with both part 1 and part 2.
- Prefer showing all cropped tasks in order:
  - Part I heading
  - tasks 1–7
  - Part II heading
  - tasks 1–5 or actual detected tasks
- If cropped tasks are missing, fall back to rendering linked original PDFs or full-page images.
- If show answer is true, right pane shows matching answer crops in the same order.

Mode: shuffle exam
- Create a “new” exam using tasks from different years.
- Total: 12 tasks.
- Prefer 7 part I tasks and 5 part II tasks.
- Mix years.
- Show tasks in exam-like order:
  - Part I
  - 7 selected part I tasks
  - Part II
  - 5 selected part II tasks
- Include a simple “reshuffle” button.
- Once generated, the exam should not change until reshuffle is clicked.
- If show answer is true, right pane shows the matching answers in the same order.

Rendering:
- For now, render generated PNG crops with simple <img> tags.
- Keep image width readable, e.g. max-width: 100%.
- Avoid fancy zoom/pan unless easy.
- Also provide links to original source PDFs near each exam/year for debugging.
- Use plain CSS.

Do not overbuild:
- No login.
- No database.
- No payments.
- No mobile design.
- No AI tutoring.
- No answer input/checking.
- No polished design system.
- No complicated backend unless necessary.
- No OCR unless the PDF has no text layer. If OCR is needed, mark that file needsReview instead of building a whole OCR pipeline.

Bun commands:
Add package scripts that are run with Bun:
- bun run dev
- bun run build
- bun run preview
- bun run fetch
- bun run extract
- bun run pipeline

The package.json scripts should look like this or very close to this:

{
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview",
    "fetch": "python scripts/fetch_materials.py",
    "extract": "python scripts/extract_tasks.py",
    "pipeline": "python scripts/run_pipeline.py"
  }
}

Use Bun for JavaScript dependency installation:
- bun install

Use Bun to add JavaScript dependencies:
- bun add <package>
- bun add -d <package>

Use Python tooling for Python dependencies:
- python -m venv .venv
- source .venv/bin/activate
- pip install -r requirements.txt

The pipeline should:
1. Fetch/download PDFs.
2. Build exams.json.
3. Extract tasks and answers.
4. Generate tasks.json.
5. Generate extraction-report.json.

README:
Write a clear README explaining:
- how to install Bun,
- how to install JavaScript dependencies with bun install,
- how to create and activate a Python venv,
- how to install Python dependencies,
- how to run bun run fetch,
- how to run bun run extract,
- how to run bun run pipeline,
- how to start the SvelteKit dev server with bun run dev,
- how to build the static site with bun run build,
- how to add a new year page in the future,
- where to manually fix task metadata if extraction is wrong.

Acceptance criteria:
- The app starts with bun run dev.
- The app builds with bun run build.
- The full data pipeline runs with bun run pipeline.
- The main page initially shows only the mode select.
- If static/data/tasks.json does not exist, the app shows:
  “No extracted tasks found yet. Run bun run pipeline.”
- No fake tasks or placeholder exams are displayed as real content.
- After bun run pipeline succeeds, the app loads real generated task data.
- Single task mode displays a random cropped task.
- Previous/next task navigation works.
- Show answer splits the page into two equal columns and shows the answer crop.
- Exam mode lets the user pick a year and shows both parts.
- Shuffle exam mode creates 12 tasks from mixed years.
- Generated JSON files are present.
- Extraction report exists and marks uncertain tasks.
- The project is simple and understandable.

Implementation priority:
1. Create the SvelteKit project using Bun.
2. Build working local SvelteKit app shell.
3. Build real loading, missing-data, and empty-data states.
4. Do not create fake task data.
5. The UI must only show real generated data from static/data/tasks.json and static/data/exams.json.
6. Build fetch script.
7. Build extraction script.
8. Connect real generated data.
9. Add fallbacks for bad crops.
10. Write README.

When making decisions, choose the simplest thing that works for a few students preparing for the exam.
