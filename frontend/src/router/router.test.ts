import { describe, expect, it } from 'vitest'
import router from './index'

describe('router', () => {
  it('registers the supported product routes', () => {
    expect(router.getRoutes().map((route) => route.path)).toEqual(
      expect.arrayContaining(['/chat', '/operations']),
    )
  })

  it('redirects the root route to chat', () => {
    expect(router.getRoutes().find((route) => route.path === '/')?.redirect).toBe('/chat')
  })

  it('keeps legacy resource bookmarks pointed at Operations', () => {
    expect(router.getRoutes().find((route) => route.path === '/repositories')?.redirect).toBe('/operations')
  })

  it('does not register a redundant standalone trace page', () => {
    expect(router.getRoutes().some((route) => route.path === '/trace')).toBe(false)
  })
})
