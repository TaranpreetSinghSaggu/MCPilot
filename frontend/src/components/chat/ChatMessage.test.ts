import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ChatMessage from './ChatMessage.vue'

describe('ChatMessage', () => {
  it('renders common Markdown and removes unsafe HTML', () => {
    const wrapper = mount(ChatMessage, {
      props: {
        role: 'assistant',
        content: '# Incident report\n\n**Resolved**\n\n| Service | Status |\n| --- | --- |\n| API | Healthy |\n\n`inline`\n\n```bash\necho ok\n```\n\n[Runbook](https://example.com)\n\n<script>alert(1)</script>',
      },
    })

    expect(wrapper.find('h1').text()).toBe('Incident report')
    expect(wrapper.find('strong').text()).toBe('Resolved')
    expect(wrapper.find('table').text()).toContain('API')
    expect(wrapper.find('code').text()).toContain('inline')
    expect(wrapper.find('pre code').text()).toContain('echo ok')
    expect(wrapper.find('a').attributes('href')).toBe('https://example.com')
    expect(wrapper.html()).not.toContain('<script>')
  })
})
