# TASKS.md

## Phase 1: Project setup
- [x] Create SvelteKit app using Bun.
- [x] Install adapter-static.
- [x] Add package scripts.
- [x] Add Python requirements.txt.

## Phase 2: App shell
- [x] Build main select: empty, single task, exam, shuffle exam.
- [x] Add show answer toggle.
- [x] Add loading / missing-data state.
- [x] Do not use fake tasks.

## Phase 3: Fetch pipeline
- [x] Fetch known year pages.
- [x] Extract PDF links.
- [x] Download relevant PDFs.
- [x] Generate exams.json.

## Phase 4: Extraction pipeline
- [x] Use PyMuPDF.
- [x] Detect task starts.
- [x] Crop task images.
- [x] Crop answer images.
- [x] Generate tasks.json and extraction-report.json.

## Phase 5: UI modes
- [x] Single task mode.
- [x] Exam mode.
- [x] Shuffle exam mode.

## Phase 6: Validation
- [x] bun run pipeline
- [x] bun run dev
- [x] bun run build
