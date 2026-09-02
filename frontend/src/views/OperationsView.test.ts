import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import OperationsView from './OperationsView.vue'
import router from '@/router'
import { api } from '@/services/api'

describe('OperationsView', () => {
  afterEach(() => vi.restoreAllMocks())

  it('renders API-backed sections and sends suggested questions to chat', async () => {
    vi.spyOn(api, 'repositories').mockResolvedValue({
      repositories: [{
        name: 'mcpilot',
        description: null,
        language: 'Python',
        team: 'Platform',
        visibility: 'private',
      }],
      count: 1,
    })
    vi.spyOn(api, 'builds').mockResolvedValue({ builds: [], count: 0 })
    vi.spyOn(api, 'slowestBuilds').mockResolvedValue({ builds: [], count: 0 })
    vi.spyOn(api, 'deployments').mockResolvedValue({ deployments: [], count: 0 })
    vi.spyOn(api, 'deploymentStats').mockResolvedValue({
      total_deployments: 0,
      successful_deployments: 0,
      failed_deployments: 0,
      average_duration_seconds: 0,
    })
    vi.spyOn(api, 'incidents').mockResolvedValue({ incidents: [], count: 0 })
    vi.spyOn(api, 'incidentStats').mockResolvedValue({
      total_incidents: 0,
      open_incidents: 0,
      resolved_incidents: 0,
      average_resolution_time_seconds: 0,
    })
    vi.spyOn(api, 'issues').mockResolvedValue({ issues: [], count: 0 })

    const wrapper = mount(OperationsView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('1 repositories')
    expect(wrapper.text()).toContain('mcpilot')

    await wrapper.get('button.question-chip').trigger('click')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/chat')
    expect(router.currentRoute.value.query.prompt).toBe('Which repositories use Python?')
    expect(router.currentRoute.value.query.new).toBe('1')
  })

  it('keeps other sections visible when one resource request fails', async () => {
    vi.spyOn(api, 'repositories').mockRejectedValue(new Error('Repositories offline'))
    vi.spyOn(api, 'builds').mockResolvedValue({ builds: [], count: 0 })
    vi.spyOn(api, 'slowestBuilds').mockResolvedValue({ builds: [], count: 0 })
    vi.spyOn(api, 'deployments').mockResolvedValue({ deployments: [], count: 0 })
    vi.spyOn(api, 'deploymentStats').mockResolvedValue({
      total_deployments: 4,
      successful_deployments: 3,
      failed_deployments: 1,
      average_duration_seconds: 12,
    })
    vi.spyOn(api, 'incidents').mockResolvedValue({ incidents: [], count: 0 })
    vi.spyOn(api, 'incidentStats').mockResolvedValue({
      total_incidents: 0,
      open_incidents: 0,
      resolved_incidents: 0,
      average_resolution_time_seconds: 0,
    })
    vi.spyOn(api, 'issues').mockResolvedValue({ issues: [], count: 0 })

    const wrapper = mount(OperationsView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Repositories offline')
    expect(wrapper.text()).toContain('75%')
    expect(wrapper.text()).toContain('3 successful')
  })
})
