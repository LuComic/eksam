<script lang="ts">
  import { appState } from "$lib/appState.svelte";
  import ExamViewer from "$lib/components/ExamViewer.svelte";
  import SearchResults from "$lib/components/SearchResults.svelte";
  import ShuffleExamViewer from "$lib/components/ShuffleExamViewer.svelte";
  import TaskAnswerRow from "$lib/components/TaskAnswerRow.svelte";
  import TaskViewer from "$lib/components/TaskViewer.svelte";
</script>

<header class="topbar">
  <div>
    {#if appState.mode === "" && !appState.searchTerm}
      <h2 class="font-semibold text-2xl mb-1.5">Vali formaat, et alustada</h2>
      <p class="warning">
        Eksamid mis on varasemad kui 2014 voivad olla buggy ja imeliku
        formaadiga
      </p>
    {:else if appState.mode === "single-task"}
      <h2 class="font-semibold text-2xl mb-1.5">Yksik ylesanne</h2>
      <p>Yks suvaline ylesanne korraga</p>
    {:else if appState.mode === "exam"}
      <h2 class="font-semibold text-2xl mb-1.5">Eksam</h2>
      <p>Kindla aasta taielik eksam</p>
    {:else if appState.mode === "shuffle-exam"}
      <h2 class="font-semibold text-2xl mb-1.5">Suvaline eksam</h2>
      <p>Tais eksam, mis koosneb erinevate aastate ylesannetest</p>
    {:else}
      <h2 class="font-semibold text-2xl mb-1.5">Otsing</h2>
    {/if}
  </div>

  {#if appState.mode === "single-task" && appState.hasTasks}
    <div class="tools nav">
      <button type="button" onclick={() => appState.previousTask()}
        >Eelmine</button
      >
      <button type="button" onclick={() => appState.nextTask()}>Jargmine</button
      >
    </div>
  {/if}
</header>

{#if appState.mode || appState.searchTerm}
  {#if appState.loading}
    <div class="empty-state"><strong>Loading materials…</strong></div>
  {:else if !appState.hasTasks}
    <div class="empty-state">
      <strong>No extracted tasks found yet. Run bun run pipeline.</strong>
    </div>
  {:else if appState.searchTerm}
    <SearchResults
      tasks={appState.searchResults}
      term={appState.searchTerm}
      onGoToExam={(task) => appState.goToExam(task)}
      onGoToTask={(task) => appState.selectTask(task)}
    />
  {:else if appState.mode === "single-task"}
    {#if appState.showAnswer}
      <TaskAnswerRow
        task={appState.currentTask}
        onGoToExam={(task) => appState.goToExam(task)}
      />
    {:else}
      <TaskViewer
        task={appState.currentTask}
        onGoToExam={(task) => appState.goToExam(task)}
      />
    {/if}
  {:else if appState.mode === "exam"}
    <ExamViewer
      tasks={appState.tasks}
      exams={appState.exams}
      showAnswers={appState.showAnswer}
      selectedYear={appState.selectedExamYear}
      onSelectionChange={(selected) => (appState.answerTasks = selected)}
    />
  {:else if appState.mode === "shuffle-exam"}
    <ShuffleExamViewer
      tasks={appState.tasks}
      showAnswers={appState.showAnswer}
      onSelectionChange={(selected) => (appState.answerTasks = selected)}
    />
  {/if}
{/if}

<style>
  h2,
  p {
    margin-top: 0;
  }

  p {
    color: var(--muted);
  }

  button {
    width: 100%;
    min-height: 34px;
    padding: 6px 8px;
    border: 1px solid var(--line);
    border-radius: 0;
    background: var(--white);
    color: var(--ink);
    font: inherit;
    cursor: pointer;
    font-weight: 700;
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

  .warning {
    color: var(--warn);
  }

  @media (max-width: 900px) {
    .topbar {
      align-items: stretch;
      flex-direction: column;
    }
  }
</style>
