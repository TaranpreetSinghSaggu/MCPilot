import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ChatTracePanel from './ChatTracePanel.vue'

describe('ChatTracePanel', () => {
  it('renders safe trace metadata for the selected response', () => {
    const wrapper = mount(ChatTracePanel, {
      props: {
        responseNumber: 2,
        trace: [
          {
            timestamp: '2026-09-01T10:00:00Z',
            event: 'llm.provider.completed',
            status: 'error',
            provider: 'gemini',
            tool_name: null,
            duration_ms: 18,
            error_code: 'RESOURCE_EXHAUSTED',
          },
        ],
      },
    })

    expect(wrapper.text()).toContain('Response 2')
    expect(wrapper.text()).toContain('gemini')
    expect(wrapper.text()).toContain('RESOURCE_EXHAUSTED')
    expect(wrapper.text()).toContain('18ms')
  })

  it('shows an empty state before a response is selected', () => {
    const wrapper = mount(ChatTracePanel, {
      props: { responseNumber: null, trace: null },
    })

    expect(wrapper.text()).toContain('Select an assistant response')
  })
})
