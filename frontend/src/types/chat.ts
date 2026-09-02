import type { ChatTurn, TraceEvent } from './api'

export interface ConversationMessage extends ChatTurn {
  id: string
  createdAt: string
  trace?: TraceEvent[]
}

export interface Conversation {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  messages: ConversationMessage[]
}

export interface StoredChatState {
  conversations: Conversation[]
  activeConversationId: string
}
