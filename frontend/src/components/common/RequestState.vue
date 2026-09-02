<script setup lang="ts">
defineProps<{ loading: boolean; error: string; empty: boolean; emptyMessage: string }>()
const emit = defineEmits<{ retry: [] }>()
</script>

<template>
  <div v-if="loading" class="space-y-3" aria-live="polite" aria-label="Loading">
    <div v-for="item in 3" :key="item" class="h-16 animate-pulse rounded-xl bg-slate-900/80" />
  </div>
  <div v-else-if="error" class="rounded-2xl border border-rose-400/20 bg-rose-400/5 p-6" role="alert">
    <p class="font-medium text-rose-100">Unable to load this view</p>
    <p class="mt-1 text-sm text-rose-200/70">{{ error }}</p>
    <button class="mt-4 rounded-lg bg-rose-200 px-3 py-2 text-sm font-semibold text-rose-950 transition hover:bg-rose-100" type="button" @click="emit('retry')">Try again</button>
  </div>
  <div v-else-if="empty" class="rounded-2xl border border-dashed border-slate-700 p-10 text-center">
    <p class="font-medium text-slate-300">{{ emptyMessage }}</p>
    <p class="mt-1 text-sm text-slate-500">There is no data to show yet.</p>
  </div>
  <slot v-else />
</template>
