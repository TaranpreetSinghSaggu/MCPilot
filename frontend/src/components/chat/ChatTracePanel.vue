<script setup lang="ts">
import StatusBadge from '@/components/common/StatusBadge.vue'
import type { TraceEvent } from '@/types/api'

defineProps<{
  trace: TraceEvent[] | null
  responseNumber: number | null
}>()

function eventLabel(event: string) {
  return event.replaceAll('.', ' ')
}

function formatTime(timestamp: string) {
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return 'Unknown time'
  return date.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}
</script>

<template>
  <aside class="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 lg:sticky lg:top-8 lg:self-start" aria-label="Execution trace">
    <div class="mb-4 flex items-start justify-between gap-3">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.18em] text-teal-300">Execution trace</p>
        <h2 class="mt-1 font-semibold text-slate-100">{{ responseNumber ? `Response ${responseNumber}` : 'Select a response' }}</h2>
      </div>
      <span class="text-xs text-slate-500">request-scoped</span>
    </div>

    <div v-if="trace === null" class="rounded-xl border border-dashed border-slate-700 p-5 text-sm leading-6 text-slate-500">
      Select an assistant response to inspect the real provider and tool steps behind it.
    </div>
    <div v-else-if="trace.length === 0" class="rounded-xl border border-dashed border-slate-700 p-5 text-sm leading-6 text-slate-500">
      This response has no trace events available.
    </div>
    <ol v-else class="space-y-3">
      <li v-for="(event, index) in trace" :key="`${event.timestamp}-${index}`" class="rounded-xl border border-slate-800/90 bg-slate-950/40 p-3">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="font-medium capitalize text-slate-200">{{ eventLabel(event.event) }}</p>
            <p class="mt-1 text-xs text-slate-500">
              {{ formatTime(event.timestamp) }}
              <span v-if="event.provider"> · {{ event.provider }}</span>
              <span v-if="event.tool_name"> · {{ event.tool_name }}</span>
            </p>
            <p v-if="event.error_code" class="mt-1 break-words text-xs text-rose-200">{{ event.error_code }}</p>
          </div>
          <StatusBadge :value="event.status" />
        </div>
        <p v-if="event.duration_ms !== null && event.duration_ms !== undefined" class="mt-2 text-right text-xs tabular-nums text-slate-500">
          {{ event.duration_ms }}ms
        </p>
      </li>
    </ol>
  </aside>
</template>
