<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ value: string | null | undefined }>()

const tone = computed(() => {
  const value = (props.value ?? '').toLowerCase()
  if (['success', 'resolved', 'merged', 'low'].includes(value)) return 'bg-teal-300/10 text-teal-200 ring-teal-300/20'
  if (['failed', 'critical', 'cancelled'].includes(value)) return 'bg-rose-300/10 text-rose-200 ring-rose-300/20'
  if (['high', 'investigating', 'in_progress', 'rolled_back'].includes(value)) return 'bg-amber-300/10 text-amber-200 ring-amber-300/20'
  return 'bg-slate-700/60 text-slate-300 ring-slate-600/60'
})
</script>

<template>
  <span class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium capitalize ring-1 ring-inset" :class="tone">
    {{ value?.replaceAll('_', ' ') || 'unknown' }}
  </span>
</template>
