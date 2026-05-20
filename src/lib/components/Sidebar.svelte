<script lang="ts">
  import { onMount } from "svelte";
  import { appState } from "$lib/appState.svelte";
  import type { Mode } from "$lib/types";

  let innerWidth = $state(0);
  const mobileBreakpoint = 900;
  const sidebarOpenStorageKey = "sidebar-open";
  let open = $state(true);

  onMount(() => {
    const savedOpen = localStorage.getItem(sidebarOpenStorageKey);
    if (savedOpen !== null) {
      open = savedOpen === "true";
    }
  });

  function setSidebarOpen(value: boolean) {
    open = value;
    localStorage.setItem(sidebarOpenStorageKey, String(value));
  }
</script>

<svelte:window bind:innerWidth />

{#if innerWidth > mobileBreakpoint}
  {#if open}
    <aside class="desktop-sidebar" aria-label="Exam browser controls">
      <button
        class="closing font-bold w-full min-h-8.5 text-xs uppercase border px-2 py-1.5 border-(--line) hover:cursor-pointer"
        onclick={() => setSidebarOpen(false)}
      >
        Sulge
      </button>
      <div class="field">
        <label for="mode">Formaat</label>
        <select
          class="w-full min-h-8.5 px-2 py-1.5 border border-(--line) rounded-none bg-(--white) text-(--ink)"
          id="mode"
          value={appState.mode}
          aria-label="mode"
          onchange={(event) =>
            appState.changeMode(
              (event.currentTarget as HTMLSelectElement).value as Mode | "",
            )}
        >
          <option value=""></option>
          <option value="single-task">Yksik ylesanne</option>
          <option value="exam">Eksam</option>
          <option value="shuffle-exam">Suvaline eksam</option>
        </select>
      </div>

      {#if appState.mode}
        <label class="check">
          <input type="checkbox" bind:checked={appState.showAnswer} />
          Naita vastuseid
        </label>
      {/if}

      <form
        class="search field"
        onsubmit={(event) => {
          event.preventDefault();
          appState.search();
        }}
      >
        <label for="search">Otsing</label>
        <div class="search-row">
          <input
            class="w-full min-h-8.5 px-2 py-1.5 border border-(--line) rounded-none bg-(--white) text-(--ink)"
            id="search"
            type="search"
            bind:value={appState.searchInput}
            aria-label="search tasks"
          />
          <button
            class="font-bold w-full min-h-8.5 text-xs uppercase border px-2 py-1.5 border-(--line) bg-(--white) text-(--ink)"
            type="submit">Otsi</button
          >
        </div>
      </form>

      <nav class="exam-list" aria-label="Available exams">
        <h3>Eksamid</h3>
        <ul>
          {#each appState.examYears as year, index (year)}
            {@const yearTasks = appState.tasksByYear.get(year) ?? []}
            {@const isExpanded = appState.expandedExamYears.includes(year)}
            <li>
              <div
                class={`exam-list-row ${index % 2 !== 0 ? "gray-bg" : null}`}
              >
                <button
                  class="year-link"
                  type="button"
                  onclick={() => appState.selectExamYear(year)}
                >
                  {year} Eksam
                </button>
                <button
                  class="expand-button"
                  type="button"
                  aria-expanded={isExpanded}
                  aria-label={`${isExpanded ? "Collapse" : "Expand"} ${year} tasks`}
                  onclick={() => appState.toggleExamYear(year)}
                >
                  &gt;
                </button>
              </div>
              {#if isExpanded}
                {#if yearTasks.length > 0}
                  <ul class="task-dropdown">
                    {#each yearTasks as task (task.id)}
                      <li>
                        <button
                          type="button"
                          onclick={() => appState.selectTask(task)}
                        >
                          Part {task.part === 1 ? "I" : "II"}, task {task.taskNumber}
                        </button>
                      </li>
                    {/each}
                  </ul>
                {:else}
                  <p class="no-year-tasks">No extracted tasks</p>
                {/if}
              {/if}
            </li>
          {/each}
        </ul>
      </nav>
    </aside>
  {:else}
    <button
      class="closing font-bold w-max min-h-8.5 h-max ml-3.5 mt-3.5 text-xs uppercase border px-2 py-1.5 border-(--line) hover:cursor-pointer top-5 left-5"
      onclick={() => setSidebarOpen(true)}>Ava</button
    >
  {/if}
{:else}
  <aside
    class="sidebar mobile-sidebar"
    aria-label="Mobile exam browser controls"
  >
    <div class="field">
      <label for="mobile-mode">Formaat</label>
      <select
        class="w-full min-h-8.5 px-2 py-1.5 border border-(--line) rounded-none bg-(--white) text-(--ink)"
        id="mobile-mode"
        value={appState.mode}
        aria-label="mode"
        onchange={(event) =>
          appState.changeMode(
            (event.currentTarget as HTMLSelectElement).value as Mode | "",
          )}
      >
        <option value=""></option>
        <option value="single-task">Yksik ylesanne</option>
        <option value="exam">Eksam</option>
        <option value="shuffle-exam">Suvaline eksam</option>
      </select>
    </div>

    {#if appState.mode}
      <label class="check">
        <input type="checkbox" bind:checked={appState.showAnswer} />
        Naita vastuseid
      </label>
    {/if}

    <form
      class="search field"
      onsubmit={(event) => {
        event.preventDefault();
        appState.search();
      }}
    >
      <label for="mobile-search">Otsing</label>
      <div class="search-row">
        <input
          class="w-full min-h-8.5 px-2 py-1.5 border border-(--line) rounded-none bg-(--white) text-(--ink)"
          id="mobile-search"
          type="search"
          bind:value={appState.searchInput}
          aria-label="search tasks"
        />
        <button
          class="font-bold w-full min-h-8.5 text-xs uppercase border px-2 py-1.5 border-(--line) bg-(--white) text-(--ink)"
          type="submit">Otsi</button
        >
      </div>
    </form>
  </aside>
{/if}

<style>
  .sidebar {
    border-right: 1px solid var(--line);
    padding: 14px;
    background: var(--white);
    width: auto;
  }

  .desktop-sidebar {
    display: flex;
    flex-direction: column;
    border-right: 1px var(--line) solid;
    padding: 14px;
    background-color: var(--white);
    gap: 14px;
    width: 350px;
    min-width: 350px;
  }

  label,
  h3,
  .field > label {
    display: block;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
  }

  .field > label:not(.check) {
    margin-bottom: 6px;
  }

  .check {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: var(--ink);
    font-size: 14px;
    text-transform: none;
  }

  .check input {
    width: 16px;
    height: 16px;
    accent-color: var(--ink);
  }

  .search-row {
    display: flex;
    gap: 6px;
  }

  .search-row input {
    min-width: 250px;
    width: 250px;
  }

  .search-row button {
    padding: 2px;
  }

  .search-row input::-webkit-search-cancel-button,
  .search-row input::-webkit-search-decoration {
    appearance: none;
    display: none;
  }

  .exam-list {
    padding-top: 12px;
    border-top: 1px solid var(--line);
  }

  .exam-list h3 {
    margin: 0 0 8px;
    font-size: 12px;
    text-transform: uppercase;
  }

  .exam-list ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .exam-list-row {
    display: flex;
    gap: 6px;
    padding-bottom: 2px;
    border-bottom: 1px var(--line) solid;
  }

  .year-link {
    min-height: auto;
    padding: 2px 0;
    border: none;
    background: transparent;
    text-align: left;
    font-weight: normal;
    width: 100%;
  }

  .expand-button {
    min-height: auto;
    padding: 0;
    border: none;
    background: transparent;
    font-weight: normal;
    text-align: right;
    margin-left: auto;
  }

  .task-dropdown {
    margin: 0 0 8px 12px !important;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .task-dropdown button {
    border-width: 0 0 1px 0;
    border-color: var(--line);
    width: 100%;
    text-align: left;
    font-size: 13px;
    font-weight: 400;
    padding-bottom: 2px;
  }

  .no-year-tasks {
    margin: 0 0 8px 12px;
    color: var(--muted);
    font-size: 13px;
  }

  .gray-bg {
    background-color: var(--soft);
  }

  .mobile-sidebar {
    order: 2;
    position: sticky;
    bottom: 0;
    z-index: 10;
    padding: 10px;
    border-right: 0;
    border-top: 1px solid var(--line);
    background: var(--white);
  }

  .mobile-sidebar .field {
    margin-bottom: 8px;
  }

  .mobile-sidebar .check {
    margin-bottom: 8px;
  }

  .mobile-sidebar .search-row input {
    min-width: 220px;
    width: 100%;
  }

  .mobile-sidebar .search-row button {
    width: 100%;
  }
</style>
