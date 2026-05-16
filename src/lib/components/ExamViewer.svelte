<script lang="ts">
  import TaskAnswerRow from './TaskAnswerRow.svelte';
  import TaskViewer from './TaskViewer.svelte';
  import type { Exam, Task } from '$lib/types';

  type Props = {
    tasks: Task[];
    exams?: Exam[];
    showYearSelect?: boolean;
    showAnswers?: boolean;
    onSelectionChange?: (tasks: Task[]) => void;
  };

  let { tasks, exams = [], showYearSelect = true, showAnswers = false, onSelectionChange }: Props = $props();
  let year = $state<number | ''>('');

  let availableYears = $derived(
    [...new Set(tasks.map((task) => task.year))].sort((a, b) => a - b)
  );
  let shownTasks = $derived(
    (year ? tasks.filter((task) => task.year === year) : [...tasks]).sort(
      (a, b) => a.part - b.part || a.taskNumber - b.taskNumber
    )
  );
  let exam = $derived(exams.find((item) => item.year === year));

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
        <option value={availableYear}>{availableYear}</option>
      {/each}
    </select>
  </label>
{/if}

{#if showYearSelect && !year}
  <p>Select a year.</p>
{:else if shownTasks.length === 0}
  <p>No extracted tasks found for this exam.</p>
{:else}
  {#if exam}
    <p class="pdfs">
      {#if exam.part1Pdf}<a href={exam.part1Pdf}>Part I PDF</a>{/if}
      {#if exam.part2Pdf}<a href={exam.part2Pdf}>Part II PDF</a>{/if}
      {#if exam.gradingPdf}<a href={exam.gradingPdf}>Grading PDF</a>{/if}
    </p>
  {/if}

  {#each [1, 2] as part}
    {@const partTasks = shownTasks.filter((task) => task.part === part)}
    {#if partTasks.length > 0}
      <h2>Part {part === 1 ? 'I' : 'II'}</h2>
      {#each partTasks as task (task.id)}
        {#if showAnswers}
          <TaskAnswerRow {task} />
        {:else}
          <TaskViewer {task} />
        {/if}
      {/each}
    {/if}
  {/each}
{/if}

<style>
  label {
    display: block;
    margin: 1rem 0;
  }

  .pdfs a {
    margin-right: 1rem;
  }
</style>
