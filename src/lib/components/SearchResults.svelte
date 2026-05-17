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
  .task-row {
    margin-bottom: 2rem;
    padding: 1rem;
  }

  .task-row.shaded {
    background: #f0f0f0;
  }
</style>
