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

<div class="container">
  <Sidebar />
  <main>
    {@render children()}
  </main>
</div>

<style>
  .container {
    min-height: 100vh;
    width: 100%;
    display: flex;
  }

  main {
    flex: 1 1 0;
    padding: 22px 28px 44px;
    background: var(--paper);
  }

  @media (max-width: 900px) {
    .container {
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
