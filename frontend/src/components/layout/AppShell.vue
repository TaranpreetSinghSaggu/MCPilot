<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppNavigation from './AppNavigation.vue'
import { api } from '@/services/api'

const mobileNavOpen = ref(false)
const healthState = ref<'checking' | 'connected' | 'unavailable'>('checking')

async function checkHealth() {
  healthState.value = 'checking'

  try {
    await api.health()
    healthState.value = 'connected'
  } catch {
    healthState.value = 'unavailable'
  }
}

onMounted(checkHealth)
</script>

<template>
  <div class="min-h-screen bg-[#08111f] text-slate-100">
    <div class="mx-auto flex min-h-screen max-w-[1600px]">
      <aside class="hidden h-screen w-64 shrink-0 overflow-y-auto border-r border-slate-800/80 px-5 py-7 md:sticky md:top-0 md:flex md:flex-col">
        <RouterLink to="/chat" class="mb-10 flex items-center gap-3 px-2" aria-label="MCPilot home">
          <span class="grid size-9 place-items-center rounded-xl bg-teal-300 font-black text-slate-950">M</span>
          <span>
            <span class="block text-sm font-semibold tracking-wide text-slate-100">MCPilot</span>
            <span class="block text-[11px] text-slate-500">DevOps intelligence</span>
          </span>
        </RouterLink>
        <AppNavigation class="flex-1" />
        <div id="chat-sidebar-slot" class="mt-8" />
        <div class="mt-auto border-t border-slate-800/80 px-2 pt-5 text-xs text-slate-500">
          <span class="mb-2 inline-flex items-center gap-2 text-slate-400" aria-live="polite">
            <span
              class="size-2 rounded-full"
              :class="healthState === 'connected' ? 'bg-teal-300' : healthState === 'unavailable' ? 'bg-rose-300' : 'bg-amber-300'"
            />
            {{ healthState === 'checking' ? 'Checking FastAPI' : healthState === 'connected' ? 'FastAPI connected' : 'FastAPI unavailable' }}
          </span>
          <button v-if="healthState === 'unavailable'" type="button" class="mb-2 block text-xs text-rose-200 underline hover:text-rose-100" @click="checkHealth">Retry health check</button>
          <p class="leading-relaxed">Ask questions in plain language. MCP-backed context stays server-side.</p>
        </div>
      </aside>

      <div class="flex min-w-0 flex-1 flex-col">
        <header class="flex items-center justify-between border-b border-slate-800/80 px-5 py-4 md:hidden">
          <RouterLink to="/chat" class="flex items-center gap-2" aria-label="MCPilot home">
            <span class="grid size-8 place-items-center rounded-lg bg-teal-300 text-sm font-black text-slate-950">M</span>
            <span class="text-sm font-semibold">MCPilot</span>
          </RouterLink>
          <button
            class="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300"
            type="button"
            :aria-expanded="mobileNavOpen"
            aria-controls="mobile-navigation"
            @click="mobileNavOpen = !mobileNavOpen"
          >
            Menu
          </button>
        </header>
        <div v-if="mobileNavOpen" id="mobile-navigation" class="border-b border-slate-800/80 px-5 py-4 md:hidden">
          <AppNavigation @navigate="mobileNavOpen = false" />
        </div>
        <main class="min-w-0 flex-1 px-5 py-6 sm:px-8 sm:py-8 lg:px-12">
          <slot />
        </main>
      </div>
    </div>
  </div>
</template>
