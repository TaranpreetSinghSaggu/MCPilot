import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import AppShell from './AppShell.vue'
import router from '@/router'
import { api } from '@/services/api'

describe('AppShell', () => {
  afterEach(() => vi.restoreAllMocks())

  it('moves from checking to connected after a successful health request', async () => {
    let resolveHealth: () => void = () => undefined
    vi.spyOn(api, 'health').mockImplementation(() => new Promise((resolve) => {
      resolveHealth = () => resolve({ status: 'ok', service: 'mcpilot' })
    }))

    const wrapper = mount(AppShell, {
      global: { plugins: [router] },
    })

    expect(wrapper.text()).toContain('Checking FastAPI')
    resolveHealth()
    await flushPromises()

    expect(wrapper.text()).toContain('FastAPI connected')
  })

  it('reports an unavailable FastAPI service and offers a retry', async () => {
    vi.spyOn(api, 'health').mockRejectedValue(new Error('offline'))

    const wrapper = mount(AppShell, {
      global: { plugins: [router] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('FastAPI unavailable')
    expect(wrapper.get('button').text()).toContain('Retry health check')
  })
})
