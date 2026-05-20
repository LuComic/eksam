<script lang="ts">
  import Sidebar from "$lib/components/Sidebar.svelte";
  import { appState } from "$lib/appState.svelte";

  let { children } = $props();

  $effect(() => {
    appState.load();
  });

  $effect(() => {
    if (
      appState.mode === "single-task" &&
      appState.hasTasks &&
      appState.shuffledTasks.length === 0
    ) {
      appState.resetSingleTask();
    }
    if (!appState.mode) {
      appState.showAnswer = false;
    }
  });
</script>

<div class="app-shell">
  <Sidebar />
  <main>
    {@render children()}
  </main>
</div>

<style>
  .app-shell {
    min-height: 100vh;
    display: flex;
  }

  main {
    padding: 22px 28px 44px;
    width: 100%;
    background: var(--paper);
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
  }
</style>
