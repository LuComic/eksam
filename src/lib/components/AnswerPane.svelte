<script lang="ts">
  import type { Task } from '$lib/types';

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
    {#each tasks as task (task.id)}
      <section>
        <h3>{task.year}, part {task.part}, task {task.taskNumber}</h3>
        {#if task.answerImagePaths.length > 0}
          {#each task.answerImagePaths as image}
            <img src={image} alt={`Answer for ${task.id}`} />
          {/each}
        {:else if task.gradingPdf}
          <p><a href={task.gradingPdf}>Open grading PDF</a></p>
          <iframe src={task.gradingPdf} title={`${task.year} grading PDF for task ${task.taskNumber}`}></iframe>
        {:else}
          <p>No grading PDF found.</p>
        {/if}
      </section>
    {/each}
  {/if}
</div>

<style>
  img {
    display: block;
    max-width: 100%;
    margin: 0 0 1rem;
    border: 1px solid #ddd;
  }

  section {
    margin-bottom: 2rem;
  }

  h3 {
    margin-top: 0;
  }

  iframe {
    width: 100%;
    height: 85vh;
    border: 1px solid #ddd;
  }
</style>
