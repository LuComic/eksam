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

<header class="topbar">
  <div>
    <h2 class="font-semibold text-2xl mb-1.5">Suvaline eksam</h2>
    <p>Tais eksam, mis koosneb erinevate aastate ylesannetest</p>
  </div>

  <button
    class="primary"
    type="button"
    onclick={reshuffle}
    disabled={tasks.length === 0}
  >
    Sega
  </button>
</header>

{#if selected.length === 0}
  <p>No extracted tasks found for shuffle exam.</p>
{:else}
  <ExamViewer tasks={selected} showYearSelect={false} {showAnswers} />
{/if}

<style>
  h2,
  p {
    margin-top: 0;
  }

  p {
    color: var(--muted);
  }

  .topbar {
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 20px;
    padding-bottom: 18px;
    margin-bottom: 22px;
    border-bottom: 1px solid var(--line);
  }

  .topbar p {
    margin-bottom: 0;
  }

  @media (max-width: 900px) {
    .topbar {
      flex-direction: column;
      align-items: start;
      width: 100%;
    }
  }

  .primary {
    width: auto;
    min-height: 34px;
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
