<script lang="ts">
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
      .sort(
        (a, b) =>
          a.part - b.part || a.year - b.year || a.taskNumber - b.taskNumber,
      );
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

<div class="app-shell">
  <aside class="sidebar" aria-label="Exam browser controls">
    <div class="field">
      <label for="mode">Mode</label>
      <select id="mode" bind:value={mode} aria-label="mode">
        <option value=""></option>
        <option value="single-task">single task</option>
        <option value="exam">exam</option>
        <option value="shuffle-exam">shuffle exam</option>
      </select>
    </div>

    {#if mode}
      <label class="check">
        <input type="checkbox" bind:checked={showAnswer} />
        answers
      </label>
    {/if}

    <form
      class="search field"
      onsubmit={(event) => {
        event.preventDefault();
        search();
      }}
    >
      <label for="search">Search</label>
      <div class="search-row">
        <input
          id="search"
          type="search"
          bind:value={searchInput}
          aria-label="search tasks"
        />
        <button type="submit">Search</button>
      </div>
    </form>

    <div class="status">
      <strong
        >{loading ? "Loading" : hasTasks ? "Data loaded" : "No data"}</strong
      >
      {tasks.length} tasks available
    </div>
  </aside>

  <main class:answers-view={showAnswer}>
    <header class="topbar">
      <div>
        {#if mode === "" && !searchTerm}
          <h2>Choose a mode</h2>
          <p>Select a mode from the sidebar to start.</p>
          <p class="warning">
            Eksamid mis on varasemad kui 2014 voivad olla buggy ja imeliku
            formaadiga
          </p>
        {:else if mode === "single-task"}
          <h2>Single task</h2>
          <p>One shuffled task at a time.</p>
        {:else if mode === "exam"}
          <h2>Exam</h2>
          <p>Pick a year and view the full exam.</p>
        {:else if mode === "shuffle-exam"}
          <h2>Shuffle exam</h2>
          <p>A new exam made from tasks across years.</p>
        {:else}
          <h2>Search results</h2>
        {/if}
      </div>

      {#if mode === "single-task" && hasTasks}
        <div class="tools nav">
          <button type="button" onclick={previousTask}>previous</button>
          <button type="button" onclick={nextTask}>next</button>
        </div>
      {/if}
    </header>

    {#if mode || searchTerm}
      {#if loading}
        <div class="empty-state"><strong>Loading materials…</strong></div>
      {:else if !hasTasks}
        <div class="empty-state">
          <strong>No extracted tasks found yet. Run bun run pipeline.</strong>
        </div>
      {:else if searchTerm}
        <SearchResults
          tasks={searchResults}
          term={searchTerm}
          onGoToExam={goToExam}
        />
      {:else if mode === "single-task"}
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
    {/if}
  </main>
</div>

<style>
  .app-shell {
    min-height: 100vh;
    display: grid;
    grid-template-columns: 300px minmax(0, 1fr);
  }

  .sidebar {
    border-right: 1px solid var(--line);
    padding: 14px;
    background: var(--white);
    width: auto;
  }

  main {
    padding: 22px 28px 44px;
    background: var(--paper);
  }

  h2,
  p {
    margin-top: 0;
  }

  h2 {
    margin-bottom: 6px;
    font-size: clamp(24px, 3vw, 34px);
    letter-spacing: -0.04em;
  }

  p {
    color: var(--muted);
  }

  label,
  .field > label {
    display: block;
    margin-bottom: 6px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .field {
    margin-bottom: 14px;
  }

  select,
  button,
  input[type="search"] {
    width: 100%;
    min-height: 34px;
    padding: 6px 8px;
    border: 1px solid var(--line);
    border-radius: 0;
    background: var(--white);
    color: var(--ink);
    font: inherit;
  }

  button {
    cursor: pointer;
    font-weight: 700;
  }

  .check {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin: 0 0 16px;
    color: var(--ink);
    font-size: 14px;
    letter-spacing: 0;
    text-transform: none;
  }

  .check input {
    width: 16px;
    height: 16px;
    accent-color: var(--ink);
  }

  .search-row {
    display: flex;
    gap: 6px;
  }

  .search-row input {
    width: 200px;
  }

  .search-row button {
    padding: 2px;
  }

  .status {
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 13px;
  }

  .status strong {
    display: block;
    margin-bottom: 4px;
    color: var(--ink);
  }

  .topbar {
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 20px;
    padding-bottom: 18px;
    margin-bottom: 22px;
    border-bottom: 1px solid var(--line);
  }

  .topbar p {
    margin-bottom: 0;
  }

  .tools {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .empty-state {
    margin-top: 28px;
    padding: 22px 0;
    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
  }

  @media (max-width: 900px) {
    .app-shell {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }

    main {
      order: 1;
      flex: 1 1 auto;
      padding: 18px;
    }

    .sidebar {
      order: 2;
      position: sticky;
      bottom: 0;
      z-index: 10;
      padding: 10px;
      border-right: 0;
      border-top: 1px solid var(--line);
      background: var(--white);
    }

    .field {
      margin-bottom: 8px;
    }

    .check {
      margin-bottom: 8px;
    }

    .status {
      display: none;
    }

    .topbar {
      align-items: stretch;
      flex-direction: column;
    }

    .search-row input {
      min-width: 300px;
    }

    .search-row button {
      width: 100%;
    }
  }

  .warning {
    color: var(--warn);
  }
</style>
