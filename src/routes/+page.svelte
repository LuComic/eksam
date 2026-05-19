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
  let expandedExamYears = $state<number[]>([]);

  let hasTasks = $derived(tasks.length > 0);
  let currentTask = $derived(shuffledTasks[currentIndex] ?? null);
  let examYears = $derived(
    Array.from({ length: 19 }, (_, index) => 2025 - index),
  );
  let tasksByYear = $derived.by(() => {
    const groups = new Map<number, Task[]>();
    for (const task of tasks) {
      const group = groups.get(task.year) ?? [];
      group.push(task);
      groups.set(task.year, group);
    }
    for (const group of groups.values()) {
      group.sort((a, b) => a.part - b.part || a.taskNumber - b.taskNumber);
    }
    return groups;
  });
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
    selectExamYear(task.year);
  }

  function selectExamYear(year: number) {
    selectedExamYear = year;
    searchInput = "";
    searchTerm = "";
    mode = "exam";
  }

  function toggleExamYear(year: number) {
    expandedExamYears = expandedExamYears.includes(year)
      ? expandedExamYears.filter((item) => item !== year)
      : [...expandedExamYears, year];
  }

  function selectTask(task: Task) {
    shuffledTasks = [
      task,
      ...shuffle(tasks.filter((item) => item.id !== task.id)),
    ];
    currentIndex = 0;
    answerTasks = [task];
    selectedExamYear = "";
    searchInput = "";
    searchTerm = "";
    mode = "single-task";
  }

  function changeMode(nextMode: Mode | "") {
    mode = nextMode;
    searchInput = "";
    searchTerm = "";
    if (nextMode !== "exam") {
      selectedExamYear = "";
    }
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
      <label for="mode">Formaat</label>
      <select
        id="mode"
        value={mode}
        aria-label="mode"
        onchange={(event) =>
          changeMode(
            (event.currentTarget as HTMLSelectElement).value as Mode | "",
          )}
      >
        <option value=""></option>
        <option value="single-task">Yksik ylesanne</option>
        <option value="exam">Eksam</option>
        <option value="shuffle-exam">Suvaline eksam</option>
      </select>
    </div>

    {#if mode}
      <label class="check">
        <input type="checkbox" bind:checked={showAnswer} />
        Naita vastuseid
      </label>
    {/if}

    <form
      class="search field"
      onsubmit={(event) => {
        event.preventDefault();
        search();
      }}
    >
      <label for="search">Otsing</label>
      <div class="search-row">
        <input
          id="search"
          type="search"
          bind:value={searchInput}
          aria-label="search tasks"
        />
        <button type="submit">Otsi</button>
      </div>
    </form>

    <nav class="exam-list" aria-label="Available exams">
      <h3>Eksamid</h3>
      <ul>
        {#each examYears as year, index (year)}
          {@const yearTasks = tasksByYear.get(year) ?? []}
          {@const isExpanded = expandedExamYears.includes(year)}
          <li>
            <div class={`exam-list-row ${index % 2 !== 0 ? "gray-bg" : null}`}>
              <button
                class="year-link"
                type="button"
                onclick={() => selectExamYear(year)}
              >
                {year} Eksam
              </button>
              <button
                class="expand-button"
                type="button"
                aria-expanded={isExpanded}
                aria-label={`${isExpanded ? "Collapse" : "Expand"} ${year} tasks`}
                onclick={() => toggleExamYear(year)}
              >
                &gt;
              </button>
            </div>
            {#if isExpanded}
              {#if yearTasks.length > 0}
                <ul class="task-dropdown">
                  {#each yearTasks as task (task.id)}
                    <li>
                      <button type="button" onclick={() => selectTask(task)}>
                        Part {task.part === 1 ? "I" : "II"}, task {task.taskNumber}
                      </button>
                    </li>
                  {/each}
                </ul>
              {:else}
                <p class="no-year-tasks">No extracted tasks</p>
              {/if}
            {/if}
          </li>
        {/each}
      </ul>
    </nav>
  </aside>

  <main class:answers-view={showAnswer}>
    <header class="topbar">
      <div>
        {#if mode === "" && !searchTerm}
          <h2>Vali formaat, et alustada</h2>
          <p class="warning">
            Eksamid mis on varasemad kui 2014 voivad olla buggy ja imeliku
            formaadiga
          </p>
        {:else if mode === "single-task"}
          <h2>Yksik ylesanne</h2>
          <p>Yks suvaline ylesanne korraga</p>
        {:else if mode === "exam"}
          <h2>Eksam</h2>
          <p>Kindla aasta taielik eksam</p>
        {:else if mode === "shuffle-exam"}
          <h2>Suvaline eksam</h2>
          <p>Tais eksam, mis koosneb erinevate aastate ylesannetest</p>
        {:else}
          <h2>Otsing</h2>
        {/if}
      </div>

      {#if mode === "single-task" && hasTasks}
        <div class="tools nav">
          <button type="button" onclick={previousTask}>Eelmine</button>
          <button type="button" onclick={nextTask}>Jargmine</button>
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
          onGoToTask={selectTask}
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
    min-width: 200px;
    width: 200px;
  }

  .search-row input::-webkit-search-cancel-button,
  .search-row input::-webkit-search-decoration {
    appearance: none;
    display: none;
  }

  .search-row button {
    padding: 2px;
  }

  .exam-list {
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--line);
  }

  .exam-list h3 {
    margin: 0 0 8px;
    font-size: 12px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .exam-list ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .exam-list-row {
    display: flex;
    gap: 6px;
    padding-bottom: 2px;
    border-bottom: 1px black solid;
  }

  .year-link {
    min-height: auto;
    padding: 2px 0 !important;
    border: 0;
    background: transparent;
    text-align: left;
    font-weight: normal;
    width: 100%;
  }

  .expand-button {
    min-height: auto;
    padding: 0 !important;
    border: 0;
    background: transparent;
    font-weight: normal;
    text-align: right;
    margin-left: auto;
  }

  .task-dropdown {
    margin: 0 0 8px 12px !important;
  }

  .task-dropdown button {
    border-width: 0 0 1px 0;
    text-align: left;
    font-size: 13px;
    font-weight: 400;
  }

  .no-year-tasks {
    margin: 0 0 8px 12px;
    color: var(--muted);
    font-size: 13px;
  }

  .gray-bg {
    background-color: var(--soft);
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

    .exam-list,
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
