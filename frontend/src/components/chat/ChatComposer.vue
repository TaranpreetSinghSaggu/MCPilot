<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{ disabled?: boolean; initialMessage?: string }>()
const emit = defineEmits<{ submit: [message: string] }>()
const message = ref('')

defineExpose({
  focus: () => document.getElementById('chat-message')?.focus(),
})

watch(
  () => props.initialMessage,
  (value) => {
    message.value = value ?? ''
  },
  { immediate: true },
)

function submit() {
  const value = message.value.trim()
  if (!value) return
  emit('submit', value)
  message.value = ''
}
</script>

<template>
  <form
    class="rounded-2xl border border-slate-700 bg-slate-900 p-2 shadow-2xl shadow-black/10"
    @submit.prevent="submit"
  >
    <label for="chat-message" class="sr-only">Ask MCPilot a question</label>
    <textarea
      id="chat-message"
      v-model="message"
      rows="2"
      :disabled="disabled"
      placeholder="Ask about your delivery system..."
      class="w-full resize-none bg-transparent px-3 py-2 text-sm leading-6 text-slate-100 placeholder:text-slate-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-60"
      @keydown.enter.exact.prevent="submit"
    />
    <div class="flex items-center justify-between gap-3 px-2 pb-1">
      <p class="text-xs text-slate-600">Enter to send · Shift + Enter for a new line</p>
      <button
        type="submit"
        :disabled="disabled || !message.trim()"
        class="rounded-xl bg-teal-300 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-teal-200 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {{ disabled ? 'Thinking…' : 'Send' }}
      </button>
    </div>
  </form>
</template>
