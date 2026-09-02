<script setup lang="ts">
const emit = defineEmits<{ prompt: [value: string] }>()

const prompts = [
  'Which repositories use Python?',
  'Show me the slowest builds.',
  'What incidents are currently open?',
]
</script>

<template>
  <section class="mx-auto flex max-w-2xl flex-col items-center py-10 text-center sm:py-16">
    <div
      class="grid size-14 place-items-center rounded-2xl bg-teal-300 text-xl font-black text-slate-950 shadow-[0_0_40px_rgba(66,217,208,0.15)]"
    >
      M
    </div>
    <p class="mt-6 text-xs font-semibold uppercase tracking-[0.2em] text-teal-300">MCPilot intelligence</p>
    <h2 class="mt-3 text-3xl font-semibold tracking-tight text-slate-100 sm:text-4xl">Ask the system behind your systems.</h2>
    <p class="mt-4 max-w-xl text-sm leading-6 text-slate-400">
      Ask about repositories, delivery health, incidents, or GitHub context.
      MCPilot gathers the operational detail and explains what matters.
    </p>
    <div class="mt-8 flex flex-wrap justify-center gap-2">
      <button
        v-for="prompt in prompts"
        :key="prompt"
        type="button"
        class="rounded-full border border-slate-700 px-3 py-2 text-xs text-slate-300 transition hover:border-teal-300/50 hover:text-teal-200"
        @click="emit('prompt', prompt)"
      >
        {{ prompt }}
      </button>
    </div>
  </section>
</template>
