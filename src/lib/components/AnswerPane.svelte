<script lang="ts">
  import type { Task } from "$lib/types";

  type Props = {
    tasks: Task[];
    showTitle?: boolean;
  };

  let { tasks, showTitle = true }: Props = $props();
</script>

<div class="answers">
  {#if showTitle}
    <h2>Grading / solutions</h2>
  {/if}
  {#if tasks.length === 0}
    <p>No answers selected.</p>
  {:else}
    {#each tasks as task, index (task.id)}
      <section>
        <h3>{task.year}, part {task.part}, task {task.taskNumber}</h3>
        {#if task.answerImagePaths.length > 0}
          {#each task.answerImagePaths as image}
            <img src={image} alt={`Answer for ${task.id}`} />
          {/each}
        {:else if task.gradingPdf}
          <p><a href={task.gradingPdf}>Open grading PDF</a></p>
          <iframe
            src={task.gradingPdf}
            title={`${task.year} grading PDF for task ${task.taskNumber}`}
          ></iframe>
        {:else}
          <p>No grading PDF found.</p>
        {/if}
      </section>
    {/each}
  {/if}
</div>

<style>
  .answers {
    padding: 18px;
    border: 1px solid var(--answer-line);
    background: var(--answers);
    color: var(--answer-ink);
  }

  section {
    margin-bottom: 24px;
  }

  h2,
  h3 {
    margin-top: 0;
    color: var(--ink);
  }

  h3 {
    padding-top: 12px;
    border-top: 1px solid var(--answer-line);
    font-size: 16px;
    text-transform: uppercase;
  }

  img {
    display: block;
    max-width: 100%;
    margin: 0 auto 1rem;
    padding: 28px;
    border: 1px solid var(--answer-line);
    border-left: 4px solid var(--answer-ink);
    background: var(--answer-paper);
  }

  iframe {
    width: 100%;
    height: 85vh;
    border: 1px solid var(--answer-line);
  }

  @media (max-width: 900px) {
    img {
      padding: 12px;
    }
  }
</style>
