export interface Repository {
  name: string
  description: string | null
  language: string
  team: string
  visibility: string
}

export interface RepositoryResponse {
  repositories: Repository[]
  count: number
}

export interface Issue {
  title: string
  repository: string
  priority: string
  status: string
  reported_by: string
  assignee: string | null
  created_at: string
  resolved_at: string | null
}

export interface IssueResponse {
  issues: Issue[]
  count: number
}

export interface Build {
  repository: string
  commit_id: number
  status: string
  duration_seconds: number
  started_at: string
  finished_at: string
}

export interface BuildResponse {
  builds: Build[]
  count: number
}

export interface Deployment {
  service: string
  commit_id: number
  environment: string
  status: string
  version: string
  duration_seconds: number
  deployed_by: string
  started_at: string
  completed_at: string
}

export interface DeploymentResponse {
  deployments: Deployment[]
  count: number
}

export interface DeploymentStats {
  total_deployments: number
  successful_deployments: number
  failed_deployments: number
  average_duration_seconds: number
}

export interface Incident {
  service: string
  title: string
  description: string
  severity: string
  status: string
  detected_at: string
  resolved_at: string | null
  root_cause: string | null
}

export interface IncidentResponse {
  incidents: Incident[]
  count: number
}

export interface IncidentStats {
  total_incidents: number
  open_incidents: number
  resolved_incidents: number
  average_resolution_time_seconds: number
}

export interface AgentResponse {
  answer: string
  trace: TraceEvent[]
}

export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
}

export interface TraceEvent {
  timestamp: string
  event: string
  status: string
  provider: string | null
  tool_name: string | null
  duration_ms: number | null
  error_code: string | null
}

export interface HealthResponse {
  status: string
  service: string
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}
