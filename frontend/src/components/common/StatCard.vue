<script setup lang="ts">
defineProps<{ label: string; value: string | number; detail?: string }>()
</script>

<template>
  <article class="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
    <p class="text-xs font-medium uppercase tracking-[0.16em] text-slate-500">{{ label }}</p>
    <p class="mt-3 text-2xl font-semibold tracking-tight text-slate-100">{{ value }}</p>
    <p v-if="detail" class="mt-1 text-xs text-slate-500">{{ detail }}</p>
  </article>
</template>
