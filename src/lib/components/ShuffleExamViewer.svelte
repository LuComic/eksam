<script lang="ts">
  import ExamViewer from './ExamViewer.svelte';
  import { buildShuffleExam } from '$lib/random';
  import type { Task } from '$lib/types';

  type Props = {
    tasks: Task[];
    showAnswers?: boolean;
    onSelectionChange?: (tasks: Task[]) => void;
  };

  let { tasks, showAnswers = false, onSelectionChange }: Props = $props();
  let selected = $state<Task[]>([]);

  function reshuffle() {
    selected = buildShuffleExam(tasks);
    onSelectionChange?.(selected);
  }

  $effect(() => {
    if (tasks.length > 0 && selected.length === 0) {
      reshuffle();
    }
  });
</script>

<button type="button" onclick={reshuffle} disabled={tasks.length === 0}>reshuffle</button>

{#if selected.length === 0}
  <p>No extracted tasks found for shuffle exam.</p>
{:else}
  <ExamViewer tasks={selected} showYearSelect={false} {showAnswers} />
{/if}
