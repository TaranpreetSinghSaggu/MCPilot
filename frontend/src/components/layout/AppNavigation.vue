<script setup lang="ts">
import { RouterLink } from 'vue-router'

const emit = defineEmits<{ navigate: [] }>()

const links = [
  { to: '/chat', label: 'Ask MCPilot', icon: '✦' },
  { to: '/operations', label: 'Operations', icon: '◈' },
]
</script>

<template>
  <nav aria-label="Primary navigation" class="flex flex-col gap-1">
    <RouterLink
      v-for="link in links"
      :key="link.to"
      :to="link.to"
      class="group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-slate-400 transition-colors hover:bg-slate-800/70 hover:text-slate-100 [&.router-link-active]:bg-teal-400/10 [&.router-link-active]:text-teal-200"
      @click="emit('navigate')"
    >
      <span aria-hidden="true" class="grid size-7 place-items-center rounded-lg bg-slate-800 text-xs text-slate-300 transition-colors group-[.router-link-active]:bg-teal-300 group-[.router-link-active]:text-slate-950">{{ link.icon }}</span>
      <span>{{ link.label }}</span>
    </RouterLink>
  </nav>
</template>
