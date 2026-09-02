import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ChatSidebar from './ChatSidebar.vue'

describe('ChatSidebar', () => {
  it('emits new chat and conversation selection actions', async () => {
    const wrapper = mount(ChatSidebar, {
      props: {
        activeConversationId: 'one',
        conversations: [
          {
            id: 'one',
            title: 'First question',
            createdAt: '2026-09-01T10:00:00Z',
            updatedAt: '2026-09-01T10:00:00Z',
            messages: [{
              id: 'message-one',
              role: 'user',
              content: 'First question',
              createdAt: '2026-09-01T10:00:00Z',
            }],
          },
        ],
      },
    })

    await wrapper.get('button').trigger('click')
    await wrapper.findAll('button')[1].trigger('click')

    expect(wrapper.emitted('newChat')).toHaveLength(1)
    expect(wrapper.emitted('selectConversation')).toEqual([['one']])
  })
})
