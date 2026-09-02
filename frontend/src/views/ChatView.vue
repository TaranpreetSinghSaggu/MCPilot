<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import ChatComposer from '@/components/chat/ChatComposer.vue'
import ChatEmptyState from '@/components/chat/ChatEmptyState.vue'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import ChatSidebar from '@/components/chat/ChatSidebar.vue'
import ChatTracePanel from '@/components/chat/ChatTracePanel.vue'
import { api } from '@/services/api'
import type { ChatTurn, TraceEvent } from '@/types/api'
import type { Conversation, ConversationMessage, StoredChatState } from '@/types/chat'

const CONVERSATIONS_KEY = 'mcpilot.chat.conversations'
const LEGACY_HISTORY_KEY = 'mcpilot.chat.history'
const TITLE_LIMIT = 56

const conversations = ref<Conversation[]>([])
const activeConversationId = ref('')
const selectedMessageId = ref<string | null>(null)
const isLoading = ref(false)
const error = ref('')
const lastQuestion = ref('')
const initialPrompt = ref('')
const composerRef = ref<{ focus: () => void } | null>(null)

function createId() {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function timestamp() {
  return new Date().toISOString()
}

function titleFromMessages(messages: ConversationMessage[]) {
  const firstQuestion = messages.find((message) => message.role === 'user')?.content.trim()
  if (!firstQuestion) return 'New chat'
  if (firstQuestion.length <= TITLE_LIMIT) return firstQuestion
  return `${firstQuestion.slice(0, TITLE_LIMIT - 1).trimEnd()}…`
}

function isTraceEvent(value: unknown): value is TraceEvent {
  if (typeof value !== 'object' || value === null) return false
  return 'timestamp' in value && typeof value.timestamp === 'string'
    && 'event' in value && typeof value.event === 'string'
    && 'status' in value && typeof value.status === 'string'
}

function isMessage(value: unknown): value is ConversationMessage {
  if (typeof value !== 'object' || value === null) return false
  if (!('role' in value) || !('content' in value)) return false
  if (value.role !== 'user' && value.role !== 'assistant') return false
  if (typeof value.content !== 'string') return false

  const id = 'id' in value && typeof value.id === 'string' ? value.id : createId()
  const createdAt = 'createdAt' in value && typeof value.createdAt === 'string'
    ? value.createdAt
    : timestamp()
  const trace = !('trace' in value) || value.trace === undefined
    ? undefined
    : Array.isArray(value.trace) && value.trace.every(isTraceEvent)
      ? value.trace
      : null

  if (trace === null) return false
  Object.assign(value, { id, createdAt, trace })
  return true
}

function createConversation(messages: ConversationMessage[] = []): Conversation {
  const now = timestamp()
  return {
    id: createId(),
    title: titleFromMessages(messages),
    createdAt: now,
    updatedAt: now,
    messages,
  }
}

function normalizeConversation(value: unknown): Conversation | null {
  if (typeof value !== 'object' || value === null) return null
  if (!('id' in value) || typeof value.id !== 'string') return null
  if (!('messages' in value) || !Array.isArray(value.messages)) return null

  const messages = value.messages.filter(isMessage)
  const now = timestamp()
  const createdAt = 'createdAt' in value && typeof value.createdAt === 'string' ? value.createdAt : now
  const updatedAt = 'updatedAt' in value && typeof value.updatedAt === 'string' ? value.updatedAt : createdAt
  return {
    id: value.id,
    title: 'title' in value && typeof value.title === 'string' ? value.title : titleFromMessages(messages),
    createdAt,
    updatedAt,
    messages,
  }
}

function readState(): StoredChatState {
  try {
    const stored = sessionStorage.getItem(CONVERSATIONS_KEY)
    if (stored) {
      const parsed = JSON.parse(stored) as unknown
      if (typeof parsed === 'object' && parsed !== null && 'conversations' in parsed && Array.isArray(parsed.conversations)) {
        const restored = parsed.conversations.map(normalizeConversation).filter((conversation): conversation is Conversation => conversation !== null)
        if (restored.length > 0) {
          const requestedActiveId = 'activeConversationId' in parsed && typeof parsed.activeConversationId === 'string'
            ? parsed.activeConversationId
            : restored[0].id
          return {
            conversations: restored,
            activeConversationId: restored.some((conversation) => conversation.id === requestedActiveId)
              ? requestedActiveId
              : restored[0].id,
          }
        }
      }
    }

    const legacy = sessionStorage.getItem(LEGACY_HISTORY_KEY)
    if (legacy) {
      const parsed = JSON.parse(legacy) as unknown
      if (Array.isArray(parsed)) {
        const messages = parsed.filter(isMessage)
        const conversation = createConversation(messages)
        return { conversations: [conversation], activeConversationId: conversation.id }
      }
    }
  } catch {
    // Stale or malformed session data is discarded safely.
  }

  const conversation = createConversation()
  return { conversations: [conversation], activeConversationId: conversation.id }
}

const restoredState = readState()
conversations.value = restoredState.conversations
activeConversationId.value = restoredState.activeConversationId

const activeConversation = computed(() => conversations.value.find((conversation) => conversation.id === activeConversationId.value) ?? null)
const messages = computed(() => activeConversation.value?.messages ?? [])
const selectedMessage = computed(() => messages.value.find((message) => message.id === selectedMessageId.value) ?? null)
const selectedTrace = computed(() => selectedMessage.value?.trace ?? null)
const selectedResponseNumber = computed(() => {
  if (!selectedMessage.value) return null
  return messages.value.slice(0, messages.value.indexOf(selectedMessage.value) + 1).filter((message) => message.role === 'assistant').length
})

watch(
  [conversations, activeConversationId],
  ([currentConversations, currentActiveId]) => {
    sessionStorage.setItem(CONVERSATIONS_KEY, JSON.stringify({
      conversations: currentConversations,
      activeConversationId: currentActiveId,
    }))
  },
  { deep: true },
)

function selectLatestTrace() {
  for (let index = messages.value.length - 1; index >= 0; index -= 1) {
    if (messages.value[index].role === 'assistant') {
      selectedMessageId.value = messages.value[index].id
      return
    }
  }
  selectedMessageId.value = null
}

function selectConversation(id: string) {
  if (id === activeConversationId.value) return
  activeConversationId.value = id
  error.value = ''
  lastQuestion.value = ''
  selectLatestTrace()
}

function newChat() {
  const conversation = createConversation()
  conversations.value.unshift(conversation)
  activeConversationId.value = conversation.id
  selectedMessageId.value = null
  error.value = ''
  lastQuestion.value = ''
  initialPrompt.value = ''
  void nextTick(() => composerRef.value?.focus())
}

function updateConversationMetadata() {
  if (!activeConversation.value) return
  activeConversation.value.title = titleFromMessages(activeConversation.value.messages)
  activeConversation.value.updatedAt = timestamp()
}

function readPrompt() {
  const params = new URLSearchParams(window.location.search)
  return {
    prompt: params.get('prompt')?.trim() ?? '',
    startsNewConversation: params.get('new') === '1',
  }
}

async function send(message: string) {
  if (isLoading.value || !activeConversation.value) return

  lastQuestion.value = message
  error.value = ''
  initialPrompt.value = ''
  const history: ChatTurn[] = activeConversation.value.messages.map(({ role, content }) => ({ role, content }))
  const userMessage: ConversationMessage = {
    id: createId(), role: 'user', content: message, createdAt: timestamp(),
  }
  activeConversation.value.messages.push(userMessage)
  updateConversationMetadata()
  isLoading.value = true

  try {
    const response = await api.chat(message, history)
    const assistantMessage: ConversationMessage = {
      id: createId(), role: 'assistant', content: response.answer, trace: response.trace, createdAt: timestamp(),
    }
    activeConversation.value.messages.push(assistantMessage)
    updateConversationMetadata()
    selectedMessageId.value = assistantMessage.id
  } catch (requestError) {
    error.value = requestError instanceof Error
      ? requestError.message
      : 'Unable to reach MCPilot right now. Please try again.'
  } finally {
    isLoading.value = false
  }
}

function retry() {
  const previous = activeConversation.value?.messages.at(-1)
  if (previous?.role === 'user' && previous.content === lastQuestion.value) {
    activeConversation.value?.messages.pop()
    updateConversationMetadata()
  }
  void send(lastQuestion.value)
}

onMounted(() => {
  const { prompt, startsNewConversation } = readPrompt()
  if (startsNewConversation) newChat()
  initialPrompt.value = prompt
  if (prompt || startsNewConversation) window.history.replaceState({}, '', window.location.pathname)
})
</script>

<template>
  <section class="mx-auto flex min-h-[calc(100vh-7rem)] max-w-[1500px] flex-col">
    <header class="mb-8 flex items-end justify-between gap-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-teal-300">DevOps intelligence</p>
        <h1 class="mt-2 text-3xl font-semibold tracking-tight text-slate-100">Ask MCPilot</h1>
      </div>
      <span class="hidden items-center gap-2 text-xs text-slate-500 sm:flex"><span class="size-2 rounded-full bg-teal-300" /> Session history enabled</span>
    </header>

    <Teleport to="#chat-sidebar-slot">
      <ChatSidebar
        :conversations="conversations"
        :active-conversation-id="activeConversationId"
        @new-chat="newChat"
        @select-conversation="selectConversation"
      />
    </Teleport>

    <div class="mb-6 lg:hidden">
      <ChatSidebar
        :conversations="conversations"
        :active-conversation-id="activeConversationId"
        @new-chat="newChat"
        @select-conversation="selectConversation"
      />
    </div>

    <div class="grid flex-1 gap-6 lg:grid-cols-[minmax(0,1fr)_20rem] lg:items-start">

      <div>
        <div v-if="messages.length === 0" class="min-h-80">
          <ChatEmptyState @prompt="send" />
        </div>
        <div v-else class="space-y-5 overflow-y-auto pb-6" aria-live="polite">
          <ChatMessage
            v-for="message in messages"
            :key="message.id"
            :role="message.role"
            :content="message.content"
            :trace-available="message.role === 'assistant' && message.trace !== undefined"
            :trace-selected="selectedMessageId === message.id"
            @select-trace="selectedMessageId = message.id"
          />
          <div v-if="isLoading" class="flex items-center gap-3 text-sm text-slate-500" role="status">
            <span class="grid size-8 place-items-center rounded-lg border border-slate-800 text-teal-300">M</span>
            MCPilot is analyzing your question…
          </div>
          <div v-if="error" class="rounded-xl border border-rose-400/20 bg-rose-400/5 p-4" role="alert">
            <p class="text-sm text-rose-100">{{ error }}</p>
            <button type="button" class="mt-3 rounded-lg bg-rose-200 px-3 py-2 text-xs font-semibold text-rose-950 hover:bg-rose-100" @click="retry">Retry</button>
          </div>
        </div>
      </div>

      <ChatTracePanel :trace="selectedTrace" :response-number="selectedResponseNumber" />
    </div>

    <div class="sticky bottom-0 mt-5 bg-[#08111f] pt-2">
      <ChatComposer ref="composerRef" :disabled="isLoading" :initial-message="initialPrompt" @submit="send" />
    </div>
  </section>
</template>
