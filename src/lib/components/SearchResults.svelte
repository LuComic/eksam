<script lang="ts">
  import TaskViewer from "./TaskViewer.svelte";
  import type { Task } from "$lib/types";

  type Props = {
    tasks: Task[];
    term: string;
    onGoToExam?: (task: Task) => void;
  };

  let { tasks, term, onGoToExam }: Props = $props();
</script>

<h2>Search for {term}</h2>

{#if tasks.length === 0}
  <p>No tasks found.</p>
{:else}
  {#each tasks as task, index (task.id)}
    <div class="task-row" class:shaded={index % 2 !== 0}>
      <TaskViewer {task} {onGoToExam} />
    </div>
  {/each}
{/if}

<style>
  h2 {
    margin: 0 0 18px;
    font-size: clamp(22px, 3vw, 30px);
    letter-spacing: -0.04em;
  }

  .task-row {
    margin-bottom: 24px;
    padding: 16px;
  }

  .task-row.shaded {
    border: 1px solid var(--line);
    background: var(--soft);
  }

  @media (max-width: 900px) {
    .task-row {
      padding: 0;
    }
  }
</style>
