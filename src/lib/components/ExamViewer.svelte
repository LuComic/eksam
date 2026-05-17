<script lang="ts">
  import TaskAnswerRow from "./TaskAnswerRow.svelte";
  import TaskViewer from "./TaskViewer.svelte";
  import type { Exam, Task } from "$lib/types";

  type Props = {
    tasks: Task[];
    exams?: Exam[];
    showYearSelect?: boolean;
    showAnswers?: boolean;
    onSelectionChange?: (tasks: Task[]) => void;
  };

  let {
    tasks,
    exams = [],
    showYearSelect = true,
    showAnswers = false,
    onSelectionChange,
  }: Props = $props();
  let year = $state<number | "">("");

  const expectedPartTasks: Record<1 | 2, number> = { 1: 7, 2: 5 };

  let availableYears = $derived(
    [
      ...new Set([
        ...tasks.map((task) => task.year),
        ...exams
          .filter(
            (exam) =>
              exam.part1Pdf ||
              exam.part2Pdf ||
              exam.gradingPdf ||
              exam.gradingDocx ||
              exam.answerTablePdf,
          )
          .map((exam) => exam.year),
      ]),
    ].sort((a, b) => a - b),
  );
  let shownTasks = $derived(
    (year ? tasks.filter((task) => task.year === year) : [...tasks]).sort(
      (a, b) => a.part - b.part || a.taskNumber - b.taskNumber,
    ),
  );
  let exam = $derived(exams.find((item) => item.year === year));
  let hasAnswerOnlyMaterial = $derived(
    !!exam &&
      shownTasks.length === 0 &&
      !!(exam.gradingPdf || exam.gradingDocx || exam.answerTablePdf),
  );
  let missingNotes = $derived.by(() => {
    if (!year) return [];
    const notes: string[] = [];
    for (const part of [1, 2] as const) {
      const partTasks = shownTasks.filter((task) => task.part === part);
      const hasPdf = part === 1 ? exam?.part1Pdf : exam?.part2Pdf;
      if (!hasPdf) {
        notes.push(
          `Could not find ${year} part ${part === 1 ? "I" : "II"} task PDF.`,
        );
        continue;
      }
      if (partTasks.length < expectedPartTasks[part]) {
        notes.push(
          `Could not find ${expectedPartTasks[part] - partTasks.length} expected ${year} part ${
            part === 1 ? "I" : "II"
          } tasks.`,
        );
      }
    }
    return notes;
  });

  function yearLabel(availableYear: number) {
    const yearTasks = tasks.filter((task) => task.year === availableYear);
    const yearExam = exams.find((item) => item.year === availableYear);
    if (yearExam?.source === "kool") {
      return `${availableYear} (${yearExam.formatNote ?? "Kool.ee materjal"})`;
    }
    if (
      yearTasks.length === 0 &&
      (yearExam?.gradingPdf ||
        yearExam?.gradingDocx ||
        yearExam?.answerTablePdf)
    ) {
      return `${availableYear} (ainult vastused)`;
    }
    return String(availableYear);
  }

  $effect(() => {
    onSelectionChange?.(shownTasks);
  });
</script>

{#if showYearSelect}
  <label>
    Year
    <select bind:value={year}>
      <option value="">Select year</option>
      {#each availableYears as availableYear}
        <option value={availableYear}>{yearLabel(availableYear)}</option>
      {/each}
    </select>
  </label>
{/if}

{#if showYearSelect && !year}
  <p>Select a year.</p>
{:else}
  {#if exam}
    <p class="pdfs">
      {#if exam.part1Pdf}<a href={exam.part1Pdf}>Part I PDF</a>{/if}
      {#if exam.part2Pdf}<a href={exam.part2Pdf}>Part II PDF</a>{/if}
      {#if exam.gradingPdf}<a href={exam.gradingPdf}>Grading PDF</a>{/if}
      {#if exam.gradingDocx}<a href={exam.gradingDocx}>Grading DOCX</a>{/if}
      {#if exam.answerTablePdf}<a href={exam.answerTablePdf}>Answer table PDF</a
        >{/if}
    </p>
    {#if exam.formatNote}
      <p class="source-note">Source note: {exam.formatNote}</p>
    {/if}
  {/if}

  {#if missingNotes.length > 0}
    <div class="notice">
      {#each missingNotes as note}
        <p>{note}</p>
      {/each}
    </div>
  {/if}

  {#if hasAnswerOnlyMaterial}
    <h2>Answers only</h2>
    <p>No extracted task PDFs were found for this exam year.</p>
    {#if exam?.gradingPdf}
      <iframe src={exam.gradingPdf} title={`${year} grading PDF`}></iframe>
    {:else if exam?.answerTablePdf}
      <iframe src={exam.answerTablePdf} title={`${year} answer table PDF`}
      ></iframe>
    {:else if exam?.gradingDocx}
      <p><a href={exam.gradingDocx}>Open grading DOCX</a></p>
    {/if}
  {:else if shownTasks.length === 0}
    <p>No extracted tasks found for this exam.</p>
  {:else}
    {#each [1, 2] as part}
      {@const partTasks = shownTasks.filter((task) => task.part === part)}
      {#if partTasks.length > 0}
        <h2>Part {part === 1 ? "I" : "II"}</h2>
        {#each partTasks as task, index (task.id)}
          {#if showAnswers}
            <div class="task-answer-pair" class:shaded={index % 2 !== 0}>
              <TaskAnswerRow {task} />
            </div>
          {:else}
            <div class="task-row" class:shaded={index % 2 !== 0}>
              <TaskViewer {task} />
            </div>
          {/if}
        {/each}
      {/if}
    {/each}
  {/if}
{/if}

<style>
  label {
    display: block;
    margin: 1rem 0;
  }

  .pdfs a {
    margin-right: 1rem;
  }

  .source-note {
    font-style: italic;
  }

  .notice {
    border: 1px solid #ccc;
    padding: 0.75rem;
    margin: 1rem 0;
  }

  .notice p {
    margin: 0 0 0.25rem;
  }

  iframe {
    width: 100%;
    height: 85vh;
    border: 1px solid #ddd;
  }

  .task-answer-pair {
    margin-bottom: 2rem;
    padding: 1rem;
  }

  .task-row {
    margin-bottom: 2rem;
    padding: 1rem;
  }

  .task-answer-pair.shaded,
  .task-row.shaded {
    background: #f0f0f0;
  }
</style>
