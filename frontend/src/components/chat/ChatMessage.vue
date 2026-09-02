<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'

const props = defineProps<{
  role: 'user' | 'assistant'
  content: string
  traceAvailable?: boolean
  traceSelected?: boolean
}>()

const emit = defineEmits<{ selectTrace: [] }>()

const renderedContent = computed(() => {
  if (props.role === 'user') return ''
  const markdown = marked.parse(props.content, { async: false })
  return DOMPurify.sanitize(markdown, {
    ALLOWED_TAGS: [
      'a', 'blockquote', 'br', 'code', 'del', 'em', 'h1', 'h2', 'h3',
      'li', 'ol', 'p', 'pre', 'strong', 'table', 'tbody', 'td', 'th',
      'thead', 'tr', 'ul',
    ],
    ALLOWED_ATTR: ['href', 'rel', 'title'],
  })
})
</script>

<template>
  <article class="flex gap-3" :class="role === 'user' ? 'justify-end' : 'justify-start'">
    <div v-if="role === 'assistant'" class="grid size-8 shrink-0 place-items-center rounded-lg bg-teal-300 text-sm font-black text-slate-950" aria-hidden="true">M</div>
    <div class="max-w-3xl rounded-2xl px-4 py-3 text-sm leading-7" :class="role === 'user' ? 'rounded-br-md bg-teal-300 text-slate-950' : 'rounded-bl-md border border-slate-800 bg-slate-900/80 text-slate-200'">
      <p v-if="role === 'user'" class="whitespace-pre-wrap">{{ content }}</p>
      <!-- The content is parsed as Markdown and sanitized with DOMPurify before insertion. -->
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div v-else class="markdown-content" v-html="renderedContent" />
      <button
        v-if="role === 'assistant' && traceAvailable"
        type="button"
        class="mt-3 inline-flex items-center rounded-md border border-slate-700 px-2.5 py-1.5 text-xs font-medium text-teal-200 transition hover:border-teal-300/60 hover:bg-teal-300/10 focus-visible:outline-teal-300"
        :aria-pressed="traceSelected"
        @click="emit('selectTrace')"
      >
        {{ traceSelected ? 'Viewing trace' : 'View trace' }}
      </button>
    </div>
  </article>
</template>
