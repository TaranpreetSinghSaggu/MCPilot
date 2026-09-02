import { afterEach, describe, expect, it, vi } from 'vitest'
import { api } from './api'

describe('api service', () => {
  afterEach(() => vi.restoreAllMocks())

  it('builds query parameters for repository filters', async () => {
    const responseBody = { repositories: [], count: 0 }
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(responseBody), { status: 200 }),
    )

    await api.repositories({ language: 'Python', team: '', visibility: 'private' })

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/repositories?language=Python&visibility=private',
      expect.objectContaining({
        headers: expect.objectContaining({ Accept: 'application/json' }),
      }),
    )
  })

  it('sends the agent message as JSON', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ answer: 'Ready.', trace: [] }), { status: 200 }),
    )

    await api.chat('What is open?')

    const expectedBody = JSON.stringify({
      message: 'What is open?',
      history: [],
    })
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/agent/chat',
      expect.objectContaining({ method: 'POST', body: expectedBody }),
    )
  })

  it('serializes prior chat turns and rejects malformed successful responses', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ answer: 'Ready.', trace: [] }), { status: 200 }),
    )
    const history = [{ role: 'user' as const, content: 'Previous question' }]

    await api.chat('Follow up', history)

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/agent/chat',
      expect.objectContaining({
        body: JSON.stringify({ message: 'Follow up', history }),
      }),
    )

    const malformedResponse = { answer: 'Missing trace' }
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify(malformedResponse), { status: 200 }),
    )
    await expect(api.chat('Malformed')).rejects.toMatchObject({
      message: 'MCPilot returned an invalid response.',
    })

    const malformedCollectionResponse = { repositories: [] }
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify(malformedCollectionResponse), { status: 200 }),
    )

    await expect(api.repositories()).rejects.toMatchObject({
      message: 'MCPilot returned an invalid response.',
    })
  })

  it('turns HTTP failures into a user-facing ApiError', async () => {
    const errorResponse = { detail: 'Nope' }
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(errorResponse), { status: 503 }),
    )

    await expect(api.health()).rejects.toMatchObject({ message: 'MCPilot is unavailable right now. Please try again.', status: 503 })
  })
})
