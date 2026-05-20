<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/state";
  import { appState } from "$lib/appState.svelte";
  import TaskAnswerRow from "$lib/components/TaskAnswerRow.svelte";
  import TaskViewer from "$lib/components/TaskViewer.svelte";

  $effect(() => {
    appState.mode = "single-task";
    const id = page.url.searchParams.get("id");
    if (!appState.hasTasks) return;

    const task = id ? appState.tasks.find((item) => item.id === id) : null;
    if (task) {
      appState.setCurrentTask(task);
    } else if (appState.shuffledTasks.length === 0) {
      appState.resetSingleTask();
      if (appState.currentTask) {
        goto(`/ylesanne?id=${encodeURIComponent(appState.currentTask.id)}`, {
          replaceState: true,
        });
      }
    }
  });
</script>

<header class="topbar">
  <div>
    <h2 class="font-semibold text-2xl mb-1.5">Yksik ylesanne</h2>
    <p>Yks suvaline ylesanne korraga</p>
  </div>

  {#if appState.hasTasks}
    <div class="tools nav">
      <button
        type="button"
        class="next-and-prev"
        onclick={() => appState.previousTask()}>Eelmine</button
      >
      <button
        type="button"
        class="next-and-prev"
        onclick={() => appState.nextTask()}>Jargmine</button
      >
    </div>
  {/if}
</header>

{#if appState.loading}
  <div class="empty-state"><strong>Loading materials…</strong></div>
{:else if !appState.hasTasks}
  <div class="empty-state">
    <strong>No extracted tasks found yet. Run bun run pipeline.</strong>
  </div>
{:else if appState.showAnswer}
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

<style>
  h2,
  p {
    margin-top: 0;
  }

  p {
    color: var(--muted);
  }

  .next-and-prev {
    width: auto;
    min-height: 34px;
    padding: 6px 10px;
    border: 1px solid var(--ink);
    border-radius: 0;
    background: var(--ink);
    color: var(--white);
    font: inherit;
    font-weight: 700;
    cursor: pointer;
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
</style>
