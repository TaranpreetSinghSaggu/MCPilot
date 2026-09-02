<script setup lang="ts">
import type { Conversation } from '@/types/chat'

defineProps<{
  conversations: Conversation[]
  activeConversationId: string
}>()

const emit = defineEmits<{
  newChat: []
  selectConversation: [id: string]
}>()

function messagePreview(conversation: Conversation) {
  const firstUserMessage = conversation.messages.find((message) => message.role === 'user')
  return firstUserMessage?.content || 'No messages yet'
}
</script>

<template>
  <section
    class="border-b border-slate-800/80 pb-5 lg:sticky lg:top-8 lg:self-start"
    aria-label="Conversations"
  >
    <div class="mb-4">
      <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
        Conversations
      </p>
      <button
        type="button"
        class="mt-3 w-full rounded-lg border border-teal-300/40 px-3 py-2 text-left text-xs font-medium text-teal-200 transition hover:bg-teal-300/10"
        @click="emit('newChat')"
      >
        + New chat
      </button>
    </div>

    <p class="mb-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-600">Recent conversations</p>
    <div v-if="conversations.length === 0" class="px-2 text-xs leading-5 text-slate-600">Your conversations will appear here.</div>
    <div v-else class="space-y-1">
      <button
        v-for="conversation in conversations"
        :key="conversation.id"
        type="button"
        class="block w-full rounded-lg px-2.5 py-2 text-left transition hover:bg-slate-800/70"
        :class="conversation.id === activeConversationId ? 'bg-teal-300/10 text-teal-100' : 'text-slate-400'"
        :aria-pressed="conversation.id === activeConversationId"
        @click="emit('selectConversation', conversation.id)"
      >
        <span class="block truncate text-xs font-medium">{{ conversation.title }}</span>
        <span class="mt-0.5 block truncate text-[11px] text-slate-600">{{ messagePreview(conversation) }}</span>
      </button>
    </div>
  </section>
</template>
