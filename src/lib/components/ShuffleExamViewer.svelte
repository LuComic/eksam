<script lang="ts">
  import ExamViewer from "./ExamViewer.svelte";
  import { buildShuffleExam } from "$lib/random";
  import type { Task } from "$lib/types";

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

<button
  class="primary"
  type="button"
  onclick={reshuffle}
  disabled={tasks.length === 0}
>
  Sega
</button>

{#if selected.length === 0}
  <p>No extracted tasks found for shuffle exam.</p>
{:else}
  <ExamViewer tasks={selected} showYearSelect={false} {showAnswers} />
{/if}

<style>
  .primary {
    width: auto;
    min-height: 34px;
    margin-bottom: 18px;
    padding: 6px 10px;
    border: 1px solid var(--ink);
    border-radius: 0;
    background: var(--ink);
    color: var(--white);
    font: inherit;
    font-weight: 700;
    cursor: pointer;
  }

  .primary:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }
</style>
