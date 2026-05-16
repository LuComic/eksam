<script lang="ts">
  import type { Task } from '$lib/types';

  type Props = {
    task: Task | null;
  };

  let { task }: Props = $props();
</script>

{#if task}
  <article class="task">
    <div class="meta">
      {task.year}, part {task.part}, task {task.taskNumber}
      {#if task.needsReview}
        <span>needs review</span>
      {/if}
    </div>
    <h2>{task.title}</h2>
    {#if task.taskImagePaths.length > 0}
      {#each task.taskImagePaths as image}
        <img src={image} alt={task.title} />
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
    margin: 0 0 0.5rem;
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
