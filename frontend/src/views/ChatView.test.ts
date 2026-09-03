import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import ChatView from './ChatView.vue'
import { api } from '@/services/api'

describe('ChatView', () => {
  beforeEach(() => {
    const sidebarTarget = document.createElement('div')
    sidebarTarget.id = 'chat-sidebar-slot'
    document.body.appendChild(sidebarTarget)
    vi.spyOn(api, 'mcpReadiness').mockResolvedValue({ status: 'ready', service: 'mcp' })
  })

  afterEach(() => {
    document.getElementById('chat-sidebar-slot')?.remove()
    sessionStorage.clear()
    window.history.replaceState({}, '', '/')
    vi.restoreAllMocks()
  })

  it('submits a question and renders the assistant answer', async () => {
    let resolveChat: (value: { answer: string; trace: [] }) => void = () => undefined
    const chat = vi.spyOn(api, 'chat').mockImplementation(
      () => new Promise((resolve) => {
        resolveChat = resolve
      }),
    )
    const wrapper = mount(ChatView)
    await flushPromises()
    const textarea = wrapper.get('textarea')

    await textarea.setValue('What is open?')
    await wrapper.get('form').trigger('submit')
    expect(wrapper.get('button[type="submit"]').text()).toContain('Thinking')
    expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeDefined()
    const response = { answer: 'There are two open incidents.', trace: [] as [] }
    resolveChat(response)
    await flushPromises()

    expect(chat).toHaveBeenCalledWith('What is open?', [])
    expect(wrapper.text()).toContain('There are two open incidents.')
    expect(wrapper.get('textarea').element.value).toBe('')
  })

  it('shows an error and exposes retry after a failed request', async () => {
    const recoveredResponse = { answer: 'Recovered.', trace: [] as [] }
    const chat = vi.spyOn(api, 'chat')
      .mockRejectedValueOnce(new Error('Service unavailable'))
      .mockResolvedValueOnce(recoveredResponse)
    const wrapper = mount(ChatView)
    await flushPromises()

    await wrapper.get('textarea').setValue('Try this')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).toContain('Service unavailable')

    await wrapper.get('[role="alert"] button').trigger('click')
    await flushPromises()
    expect(chat).toHaveBeenCalledTimes(2)
    expect(wrapper.text()).toContain('Recovered.')
    expect(wrapper.findAll('article').filter((message) => message.text() === 'Try this')).toHaveLength(1)
  })

  it('starts MCP readiness on mount and disables the composer until it succeeds', async () => {
    let resolveReadiness: (value: { status: string; service: string }) => void = () => undefined
    const readiness = vi.mocked(api.mcpReadiness)
    readiness.mockImplementationOnce(() => new Promise((resolve) => {
      resolveReadiness = resolve
    }))
    const chat = vi.spyOn(api, 'chat')
    const wrapper = mount(ChatView)

    expect(readiness).toHaveBeenCalledOnce()
    expect(wrapper.get('[role="status"]').text()).toContain('Connecting to MCPilot tools')
    expect(wrapper.get('textarea').attributes('disabled')).toBeDefined()
    await wrapper.get('form').trigger('submit')
    expect(chat).not.toHaveBeenCalled()

    resolveReadiness({ status: 'ready', service: 'mcp' })
    await flushPromises()

    expect(wrapper.find('[role="status"]').exists()).toBe(false)
    expect(wrapper.get('textarea').attributes('disabled')).toBeUndefined()
  })

  it('shows readiness failure and retries readiness without creating a chat message', async () => {
    const readiness = vi.mocked(api.mcpReadiness)
    const chat = vi.spyOn(api, 'chat')
    readiness
      .mockRejectedValueOnce(new Error('MCP service did not become ready within 2 minutes.'))
      .mockResolvedValueOnce({ status: 'ready', service: 'mcp' })
    const wrapper = mount(ChatView)
    await flushPromises()

    expect(wrapper.get('[role="alert"]').text()).toContain('MCP service did not become ready within 2 minutes.')
    expect(wrapper.get('[role="alert"] button').text()).toContain('Retry readiness')
    expect(wrapper.get('textarea').attributes('disabled')).toBeDefined()
    expect(wrapper.text()).not.toContain('Try this')
    expect(chat).not.toHaveBeenCalled()

    await wrapper.get('[role="alert"] button').trigger('click')
    await flushPromises()

    expect(readiness).toHaveBeenCalledTimes(2)
    expect(wrapper.get('textarea').attributes('disabled')).toBeUndefined()
    expect(wrapper.text()).not.toContain('MCP service did not become ready')
    expect(chat).not.toHaveBeenCalled()
  })

  it('restores the transcript after the route component is remounted', async () => {
    const response = { answer: 'This remains in the session.', trace: [] as [] }
    vi.spyOn(api, 'chat').mockResolvedValue(response)
    const first = mount(ChatView)
    await flushPromises()
    await first.get('textarea').setValue('Remember this')
    await first.get('form').trigger('submit')
    await flushPromises()
    first.unmount()

    const second = mount(ChatView)
    await flushPromises()
    expect(second.text()).toContain('This remains in the session.')
  })

  it('sends visible prior turns as context for a follow-up question', async () => {
    const firstResponse = { answer: 'First answer', trace: [] as [] }
    const followUpResponse = { answer: 'Follow-up answer', trace: [] as [] }
    const chat = vi.spyOn(api, 'chat')
      .mockResolvedValueOnce(firstResponse)
      .mockResolvedValueOnce(followUpResponse)
    const wrapper = mount(ChatView)
    await flushPromises()

    await wrapper.get('textarea').setValue('First question')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    await wrapper.get('textarea').setValue('Follow up')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(chat).toHaveBeenNthCalledWith(2, 'Follow up', [
      { role: 'user', content: 'First question' },
      { role: 'assistant', content: 'First answer' },
    ])
  })

  it('prepares a suggested question from the Operations link', async () => {
    window.history.replaceState({}, '', '/chat?prompt=Which%20builds%20are%20slowest%3F')

    const wrapper = mount(ChatView)
    await flushPromises()

    expect(wrapper.get('textarea').element.value).toBe('Which builds are slowest?')
  })

  it('associates the returned trace with the assistant response', async () => {
    const response = {
      answer: 'The service is healthy.',
      trace: [{
        timestamp: '2026-09-01T10:00:00Z',
        event: 'llm.provider.completed',
        status: 'success',
        provider: 'groq',
        tool_name: null,
        duration_ms: 24,
        error_code: null,
      }],
    }
    vi.spyOn(api, 'chat').mockResolvedValue(response)
    const wrapper = mount(ChatView)
    await flushPromises()

    await wrapper.get('textarea').setValue('Is the service healthy?')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('The service is healthy.')
    expect(wrapper.text()).toContain('groq')
    expect(wrapper.text()).toContain('24ms')
  })

  it('keeps conversations isolated when a new chat is created', async () => {
    const firstResponse = { answer: 'First answer', trace: [] as [] }
    const secondResponse = { answer: 'Second answer', trace: [] as [] }
    const chat = vi.spyOn(api, 'chat')
      .mockResolvedValueOnce(firstResponse)
      .mockResolvedValueOnce(secondResponse)
    const wrapper = mount(ChatView)
    await flushPromises()

    await wrapper.get('textarea').setValue('First question')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    await wrapper.get('section[aria-label="Conversations"] button').trigger('click')
    expect(wrapper.text()).toContain('First question')

    await wrapper.get('textarea').setValue('Second question')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(chat).toHaveBeenNthCalledWith(2, 'Second question', [])

    const previousConversation = wrapper.findAll('section[aria-label="Conversations"] button')
      .find((button) => button.text().includes('First question'))
    await previousConversation?.trigger('click')

    expect(wrapper.text()).toContain('First answer')
    expect(wrapper.text()).not.toContain('Second answer')
  })
})
