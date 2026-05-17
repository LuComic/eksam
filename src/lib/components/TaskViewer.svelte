<script lang="ts">
  import { taskDisplayTitle } from '$lib/taskLabels';
  import type { Task } from '$lib/types';

  type Props = {
    task: Task | null;
    onGoToExam?: (task: Task) => void;
  };

  let { task, onGoToExam }: Props = $props();
  let title = $derived(task ? taskDisplayTitle(task) : '');
  let reviewLabel = $derived(task && task.year < 2014 ? 'might be buggy' : 'needs review');
</script>

{#if task}
  <article class="task">
    <div class="meta">
      <span class="task-label">{task.year}, part {task.part}, task {task.taskNumber}</span>
      {#if onGoToExam}
        <button type="button" onclick={() => onGoToExam?.(task)}>go to exam</button>
      {/if}
      {#if task.needsReview}
        <span>{reviewLabel}</span>
      {/if}
    </div>
    <h2>{title}</h2>
    {#if task.taskImagePaths.length > 0}
      {#each task.taskImagePaths as image}
        <img src={image} alt={title} />
      {/each}
    {:else}
      <p>No task crop found.</p>
      {#if task.sourcePdf}
        <p><a href={task.sourcePdf}>Open source PDF</a></p>
      {/if}
    {/if}
  </article>
{:else}
  <p>No task selected.</p>
{/if}

<style>
  .meta {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin: 0 0 0.5rem;
  }

  .task-label {
    margin-left: 0;
    font-size: 1rem;
    color: inherit;
  }

  span {
    margin-left: 0.5rem;
    font-size: 0.85rem;
    color: #8a5a00;
  }

  img {
    display: block;
    max-width: 100%;
    margin: 0 0 1rem;
    border: 1px solid #ddd;
  }
</style>
