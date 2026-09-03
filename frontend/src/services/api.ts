import type {
  AgentResponse,
  BuildResponse,
  DeploymentResponse,
  DeploymentStats,
  HealthResponse,
  IncidentResponse,
  IncidentStats,
  IssueResponse,
  MCPReadinessResponse,
  RepositoryResponse,
  ChatTurn,
} from '@/types/api'
import { ApiError } from '@/types/api'

const baseUrl = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

function queryString(values: Record<string, string | number | undefined>): string {
  const params = new URLSearchParams()

  for (const [key, value] of Object.entries(values)) {
    if (value !== undefined && value !== '') {
      params.set(key, String(value))
    }
  }

  const result = params.toString()
  return result ? `?${result}` : ''
}

type PayloadValidator = (payload: unknown) => boolean
type RequestOptions = { preserveServerErrorDetail?: boolean }

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function hasCollectionField(field: string): PayloadValidator {
  return (payload) => isRecord(payload)
    && Array.isArray(payload[field])
    && typeof payload.count === 'number'
}

function hasNumberFields(...fields: string[]): PayloadValidator {
  return (payload) => isRecord(payload) && fields.every((field) => typeof payload[field] === 'number')
}

async function request<T>(
  path: string,
  init?: RequestInit,
  validate: PayloadValidator = isRecord,
  options: RequestOptions = {},
): Promise<T> {
  let response: Response

  try {
    response = await fetch(`${baseUrl}${path}`, {
      ...init,
      headers: {
        Accept: 'application/json',
        ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
        ...init?.headers,
      },
    })
  } catch {
    throw new ApiError('Unable to reach MCPilot right now. Please try again.')
  }

  const text = await response.text()
  if (!text) {
    throw new ApiError('MCPilot returned an empty response.', response.status)
  }

  let payload: unknown

  try {
    payload = JSON.parse(text)
  } catch {
    throw new ApiError('MCPilot returned an invalid response.', response.status)
  }

  if (!response.ok) {
    const responseDetail = typeof payload === 'object' && payload !== null && 'detail' in payload
      ? String(payload.detail)
      : 'The request could not be completed.'
    const detail = response.status >= 500 && !options.preserveServerErrorDetail
      ? 'MCPilot is unavailable right now. Please try again.'
      : responseDetail
    throw new ApiError(detail, response.status)
  }

  if (!validate(payload)) {
    throw new ApiError('MCPilot returned an invalid response.', response.status)
  }

  return payload as T
}

export const api = {
  health(): Promise<HealthResponse> {
    return request<HealthResponse>(
      '/health',
      undefined,
      (payload) => isRecord(payload)
        && typeof payload.status === 'string'
        && typeof payload.service === 'string',
    )
  },

  mcpReadiness(signal?: AbortSignal): Promise<MCPReadinessResponse> {
    return request<MCPReadinessResponse>(
      '/api/agent/readiness',
      { signal },
      (payload) => isRecord(payload)
        && payload.status === 'ready'
        && payload.service === 'mcp',
      { preserveServerErrorDetail: true },
    )
  },

  chat(message: string, history: ChatTurn[] = []): Promise<AgentResponse> {
    return request<AgentResponse>('/api/agent/chat', {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    }, (payload) => isRecord(payload) && typeof payload.answer === 'string' && Array.isArray(payload.trace))
  },

  repositories(filters: {
    language?: string
    team?: string
    visibility?: string
  } = {}): Promise<RepositoryResponse> {
    return request<RepositoryResponse>(
      `/api/repositories${queryString(filters)}`,
      undefined,
      hasCollectionField('repositories'),
    )
  },

  issues(filters: {
    repository_name?: string
    priority?: string
    status?: string
    assignee_username?: string
  } = {}): Promise<IssueResponse> {
    return request<IssueResponse>(`/api/issues${queryString(filters)}`, undefined, hasCollectionField('issues'))
  },

  builds(filters: {
    repository_name?: string
    status?: string
  } = {}): Promise<BuildResponse> {
    return request<BuildResponse>(`/api/builds${queryString(filters)}`, undefined, hasCollectionField('builds'))
  },

  slowestBuilds(repository_name?: string): Promise<BuildResponse> {
    return request<BuildResponse>(
      `/api/builds/slowest${queryString({ repository_name })}`,
      undefined,
      hasCollectionField('builds'),
    )
  },

  deployments(filters: {
    service_name?: string
    environment?: string
    status?: string
  } = {}): Promise<DeploymentResponse> {
    return request<DeploymentResponse>(
      `/api/deployments${queryString(filters)}`,
      undefined,
      hasCollectionField('deployments'),
    )
  },

  deploymentStats(filters: {
    service_name?: string
    environment?: string
  } = {}): Promise<DeploymentStats> {
    return request<DeploymentStats>(
      `/api/deployments/stats${queryString(filters)}`,
      undefined,
      hasNumberFields('total_deployments', 'successful_deployments', 'failed_deployments', 'average_duration_seconds'),
    )
  },

  incidents(filters: {
    service_name?: string
    severity?: string
    status?: string
  } = {}): Promise<IncidentResponse> {
    return request<IncidentResponse>(`/api/incidents${queryString(filters)}`, undefined, hasCollectionField('incidents'))
  },

  incidentStats(service_name?: string): Promise<IncidentStats> {
    return request<IncidentStats>(
      `/api/incidents/stats${queryString({ service_name })}`,
      undefined,
      hasNumberFields('total_incidents', 'open_incidents', 'resolved_incidents', 'average_resolution_time_seconds'),
    )
  },
}

export { queryString, request }
