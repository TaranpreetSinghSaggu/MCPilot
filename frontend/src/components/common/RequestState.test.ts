import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import RequestState from './RequestState.vue'

describe('RequestState', () => {
  it('distinguishes an empty result from a loading result', () => {
    const empty = mount(RequestState, { props: { loading: false, error: '', empty: true, emptyMessage: 'Nothing here.' } })
    expect(empty.text()).toContain('Nothing here.')

    const loading = mount(RequestState, { props: { loading: true, error: '', empty: false, emptyMessage: 'Nothing here.' } })
    expect(loading.find('[aria-label="Loading"]').exists()).toBe(true)
  })
})
