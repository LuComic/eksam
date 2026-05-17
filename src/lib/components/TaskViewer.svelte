<script lang="ts">
  import { taskDisplayTitle } from "$lib/taskLabels";
  import type { Task } from "$lib/types";

  type Props = {
    task: Task | null;
    onGoToExam?: (task: Task) => void;
  };

  let { task, onGoToExam }: Props = $props();
  let title = $derived(task ? taskDisplayTitle(task) : "");
  let reviewLabel = $derived(
    task && task.year < 2014 ? "might be buggy" : "needs review",
  );
</script>

{#if task}
  <article class="task-block">
    <div class="task-head">
      <div class="num">{task.taskNumber}</div>
      <div class="task-title">
        <strong>{title}</strong>
      </div>
      {#if task.needsReview}
        <span class="pill review">{reviewLabel}</span>
      {/if}
    </div>
    <div class="meta-strip">
      {#if onGoToExam}
        <button type="button" onclick={() => onGoToExam?.(task)}
          >go to exam</button
        >
      {/if}
    </div>
    {#if task.taskImagePaths.length > 0}
      {#each task.taskImagePaths as image}
        <div class="pdf-crop"><img src={image} alt={title} /></div>
      {/each}
    {:else}
      <div class="pdf-crop">
        <p>No task crop found.</p>
        {#if task.sourcePdf}
          <p><a href={task.sourcePdf}>Open source PDF</a></p>
        {/if}
      </div>
    {/if}
  </article>
{:else}
  <p>No task selected.</p>
{/if}

<style>
  .task-block {
    margin-bottom: 24px;
  }

  .task-head {
    display: grid;
    grid-template-columns: 52px 1fr auto;
    gap: 12px;
    align-items: center;
    margin-bottom: 10px;
  }

  .num {
    display: grid;
    place-items: center;
    height: 38px;
    border: 1px solid var(--line);
    background: var(--white);
    font-size: 18px;
    font-weight: 800;
  }

  .task-title strong {
    display: block;
    font-size: 18px;
  }

  .task-title span {
    color: var(--muted);
    font-size: 14px;
  }

  .meta-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 18px;
  }

  .pill,
  button {
    display: inline-flex;
    align-items: center;
    min-height: 28px;
    padding: 4px 9px;
    border: 1px solid var(--line);
    background: var(--white);
    color: var(--ink);
    font: inherit;
    font-size: 13px;
    font-weight: 700;
  }

  button {
    cursor: pointer;
  }

  .pill.review {
    color: var(--warn);
    border-color: var(--warn);
  }

  .pdf-crop {
    margin-bottom: 16px;
    padding: 28px;
    border: 1px solid var(--line);
    background: var(--white);
  }

  img {
    display: block;
    max-width: 100%;
    margin: 0 auto;
  }

  @media (max-width: 900px) {
    .task-head {
      grid-template-columns: 52px 1fr;
    }

    .task-head .pill {
      grid-column: 1 / -1;
      width: fit-content;
    }

    .pdf-crop {
      padding: 12px;
    }
  }
</style>
