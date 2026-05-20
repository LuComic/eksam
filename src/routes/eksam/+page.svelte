<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/state";
  import { appState } from "$lib/appState.svelte";
  import ExamViewer from "$lib/components/ExamViewer.svelte";
  import ShuffleExamViewer from "$lib/components/ShuffleExamViewer.svelte";

  let isShuffle = $derived(
    page.url.searchParams.get("type") === "shuffle-exam",
  );
  let yearParam = $derived(page.url.searchParams.get("year"));
  let selectedYear: number | "" = $derived(yearParam ? Number(yearParam) : "");

  $effect(() => {
    appState.mode = isShuffle ? "shuffle-exam" : "exam";
    appState.searchTerm = "";
    appState.selectedExamYear = selectedYear || "";
  });
</script>

<header class="topbar">
  <div>
    {#if isShuffle}
      <h2 class="font-semibold text-2xl mb-1.5">Suvaline eksam</h2>
      <p>Tais eksam, mis koosneb erinevate aastate ylesannetest</p>
    {:else}
      <h2 class="font-semibold text-2xl mb-1.5">Eksam</h2>
      <p>Kindla aasta taielik eksam</p>
    {/if}
  </div>
</header>

{#if appState.loading}
  <div class="empty-state"><strong>Loading materials…</strong></div>
{:else if !appState.hasTasks}
  <div class="empty-state">
    <strong>No extracted tasks found yet. Run bun run pipeline.</strong>
  </div>
{:else if isShuffle}
  <ShuffleExamViewer
    tasks={appState.tasks}
    showAnswers={appState.showAnswer}
    onSelectionChange={(selected) => (appState.answerTasks = selected)}
  />
{:else}
  <ExamViewer
    tasks={appState.tasks}
    exams={appState.exams}
    showAnswers={appState.showAnswer}
    {selectedYear}
    onSelectionChange={(selected) => (appState.answerTasks = selected)}
    onYearChange={(year) => goto(year ? `/eksam?year=${year}` : "/eksam")}
  />
{/if}

<style>
  h2,
  p {
    margin-top: 0;
  }
  p {
    color: var(--muted);
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
  .empty-state {
    margin-top: 28px;
    padding: 22px 0;
    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
  }
</style>
