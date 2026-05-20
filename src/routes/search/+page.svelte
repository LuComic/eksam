<script lang="ts">
  import { page } from "$app/state";
  import { appState } from "$lib/appState.svelte";
  import SearchResults from "$lib/components/SearchResults.svelte";

  let term = $derived(page.url.searchParams.get("q") ?? "");

  $effect(() => {
    appState.mode = "";
    appState.searchInput = term;
    appState.searchTerm = term;
  });
</script>

<header class="topbar">
  <div>
    <h2 class="font-semibold text-2xl mb-1.5">Otsing</h2>
  </div>
</header>

{#if appState.loading}
  <div class="empty-state"><strong>Loading materials…</strong></div>
{:else if !appState.hasTasks}
  <div class="empty-state">
    <strong>No extracted tasks found yet. Run bun run pipeline.</strong>
  </div>
{:else}
  <SearchResults
    tasks={appState.searchResults}
    term={appState.searchTerm}
    onGoToExam={(task) => appState.goToExam(task)}
    onGoToTask={(task) => appState.selectTask(task)}
  />
{/if}

<style>
  h2 {
    margin-top: 0;
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

  @media (max-width: 900px) {
    .topbar {
      flex-direction: column;
      align-items: start;
      width: 100%;
    }
  }

  .empty-state {
    margin-top: 28px;
    padding: 22px 0;
    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
  }
</style>
