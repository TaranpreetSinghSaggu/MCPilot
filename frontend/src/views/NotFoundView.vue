<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <section class="mx-auto flex min-h-[60vh] max-w-xl flex-col items-center justify-center text-center">
    <p class="text-xs font-semibold uppercase tracking-[0.2em] text-teal-300">
      404 · Unknown route
    </p>
    <h1 class="mt-3 text-3xl font-semibold tracking-tight text-slate-100">
      That signal is not on the map.
    </h1>
    <p class="mt-3 text-sm leading-6 text-slate-400">
      Return to MCPilot and ask a question, or choose an operational view from
      the navigation.
    </p>
    <RouterLink
      to="/chat"
      class="mt-6 rounded-xl bg-teal-300 px-4 py-2.5 text-sm font-semibold text-slate-950 hover:bg-teal-200"
    >
      Go to chat
    </RouterLink>
  </section>
</template>
