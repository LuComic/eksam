<script lang="ts">
  import AnswerPane from './AnswerPane.svelte';
  import TaskViewer from './TaskViewer.svelte';
  import type { Task } from '$lib/types';

  type Props = {
    task: Task | null;
  };

  let { task }: Props = $props();
</script>

<div class="row">
  <div>
    <TaskViewer {task} />
  </div>
  <div>
    <AnswerPane tasks={task ? [task] : []} showTitle={false} />
  </div>
</div>

<style>
  .row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 1rem;
    align-items: start;
  }
</style>
