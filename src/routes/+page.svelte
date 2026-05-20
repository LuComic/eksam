<script lang="ts">
  import { appState } from "$lib/appState.svelte";

  $effect(() => {
    appState.mode = "";
    appState.searchTerm = "";
  });
</script>

<header class="topbar">
  <div>
    <h2 class="font-semibold text-2xl mb-1.5">Vali formaat, et alustada</h2>
    <p class="warning">
      Eksamid mis on varasemad kui 2014 voivad olla buggy ja imeliku formaadiga
    </p>
  </div>
</header>

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

  .warning {
    color: var(--warn);
  }
</style>
