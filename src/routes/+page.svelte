<script lang="ts">
  import AnswerPane from "$lib/components/AnswerPane.svelte";
  import ExamViewer from "$lib/components/ExamViewer.svelte";
  import SearchResults from "$lib/components/SearchResults.svelte";
  import ShuffleExamViewer from "$lib/components/ShuffleExamViewer.svelte";
  import TaskAnswerRow from "$lib/components/TaskAnswerRow.svelte";
  import TaskViewer from "$lib/components/TaskViewer.svelte";
  import { loadMaterials } from "$lib/data";
  import { shuffle } from "$lib/random";
  import { taskDisplayTitle } from "$lib/taskLabels";
  import type { Exam, Mode, Task } from "$lib/types";

  let mode = $state<Mode | "">("");
  let showAnswer = $state(false);
  let loading = $state(true);
  let tasks = $state<Task[]>([]);
  let exams = $state<Exam[]>([]);
  let shuffledTasks = $state<Task[]>([]);
  let currentIndex = $state(0);
  let answerTasks = $state<Task[]>([]);
  let searchInput = $state("");
  let searchTerm = $state("");
  let selectedExamYear = $state<number | "">("");

  let hasTasks = $derived(tasks.length > 0);
  let currentTask = $derived(shuffledTasks[currentIndex] ?? null);
  let searchResults = $derived.by(() => {
    const term = searchTerm.trim().toLowerCase();
    if (!term) return [];

    return tasks
      .filter((task) => {
        const searchable = [
          task.id,
          taskDisplayTitle(task),
          String(task.year),
          `part ${task.part}`,
          `task ${task.taskNumber}`,
          `${task.year} ${task.part} ${task.taskNumber}`,
        ]
          .join(" ")
          .toLowerCase();

        return searchable.includes(term);
      })
      .sort((a, b) => a.part - b.part || a.year - b.year || a.taskNumber - b.taskNumber);
  });

  async function load() {
    loading = true;
    const materials = await loadMaterials();
    tasks = materials.tasks;
    exams = materials.exams;
    loading = false;
  }

  function resetSingleTask() {
    shuffledTasks = shuffle(tasks);
    currentIndex = 0;
    answerTasks = shuffledTasks[0] ? [shuffledTasks[0]] : [];
  }

  function previousTask() {
    if (shuffledTasks.length === 0) return;
    currentIndex =
      (currentIndex - 1 + shuffledTasks.length) % shuffledTasks.length;
    answerTasks = currentTask ? [currentTask] : [];
  }

  function nextTask() {
    if (shuffledTasks.length === 0) return;
    currentIndex = (currentIndex + 1) % shuffledTasks.length;
    answerTasks = currentTask ? [currentTask] : [];
  }

  function search() {
    searchTerm = searchInput.trim();
  }

  function goToExam(task: Task) {
    selectedExamYear = task.year;
    searchTerm = "";
    mode = "exam";
  }

  $effect(() => {
    load();
  });

  $effect(() => {
    if (mode === "single-task" && hasTasks && shuffledTasks.length === 0) {
      resetSingleTask();
    }
    if (!mode) {
      showAnswer = false;
      searchInput = "";
      searchTerm = "";
    }
  });
</script>

<main>
  <div class="controls">
    {#if mode === ""}
      <span>Vali ylesande tyyp</span>
    {:else if mode === "single-task"}
      <span class="bold">Single task - yhe suvalise ylesande kaupa</span>
    {:else if mode === "exam"}
      <span class="bold">Exam - vali tapne eksam</span>
    {:else}
      <span class="bold"> Suvaline eksam erinevate eksamite ylesannetest </span>
    {/if}
    <select bind:value={mode} aria-label="mode">
      <option value=""></option>
      <option value="single-task">single task</option>
      <option value="exam">exam</option>
      <option value="shuffle-exam">shuffle exam</option>
    </select>

    <form
      class="search"
      onsubmit={(event) => {
        event.preventDefault();
        search();
      }}
    >
      <input type="search" bind:value={searchInput} aria-label="search tasks" />
      <button type="submit">search</button>
    </form>

    {#if mode}
      <label>
        <input type="checkbox" bind:checked={showAnswer} />
        show answer
      </label>
    {/if}
  </div>

  {#if mode || searchTerm}
    {#if loading}
      <p>Loading materials…</p>
    {:else if !hasTasks}
      <p>No extracted tasks found yet. Run bun run pipeline.</p>
    {:else}
      <div>
        {#if searchTerm}
          <SearchResults tasks={searchResults} term={searchTerm} onGoToExam={goToExam} />
        {:else if mode === "single-task"}
          <div class="nav">
            <button type="button" onclick={previousTask}>previous</button>
            <button type="button" onclick={nextTask}>next</button>
          </div>
          {#if showAnswer}
            <TaskAnswerRow task={currentTask} onGoToExam={goToExam} />
          {:else}
            <TaskViewer task={currentTask} onGoToExam={goToExam} />
          {/if}
        {:else if mode === "exam"}
          <ExamViewer
            {tasks}
            {exams}
            showAnswers={showAnswer}
            selectedYear={selectedExamYear}
            onSelectionChange={(selected) => (answerTasks = selected)}
          />
        {:else if mode === "shuffle-exam"}
          <ShuffleExamViewer
            {tasks}
            showAnswers={showAnswer}
            onSelectionChange={(selected) => (answerTasks = selected)}
          />
        {/if}
      </div>
    {/if}
  {/if}
</main>

<style>
  main {
    padding: 1rem;
    font-family: system-ui, sans-serif;
  }

  .controls {
    display: flex;
    gap: 1rem;
    align-items: center;
    margin-bottom: 1rem;
  }

  .nav {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .search {
    display: flex;
    gap: 0.5rem;
  }

  .bold {
    font-weight: 600;
  }
</style>
