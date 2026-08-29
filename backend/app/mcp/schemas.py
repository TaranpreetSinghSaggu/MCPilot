from pydantic import BaseModel


class Repository(BaseModel):
    name: str
    description: str
    language: str
    team: str
    visibility: str


class RepositorySearchResult(BaseModel):
    repositories: list[Repository]
    count: int


class Issue(BaseModel):
    title: str
    repository: str
    priority: str
    status: str
    reported_by: str
    assignee: str | None
    created_at: str
    resolved_at: str | None


class IssueSearchResult(BaseModel):
    issues: list[Issue]
    count: int


class Build(BaseModel):
    repository: str
    commit_id: int
    status: str
    duration_seconds: float
    started_at: str
    finished_at: str


class BuildSearchResult(BaseModel):
    builds: list[Build]
    count: int


class Deployment(BaseModel):
    service: str
    commit_id: int
    environment: str
    status: str
    version: str
    duration_seconds: float
    deployed_by: str
    started_at: str
    completed_at: str


class DeploymentSearchResult(BaseModel):
    deployments: list[Deployment]
    count: int


class DeploymentStats(BaseModel):
    total_deployments: int
    successful_deployments: int
    failed_deployments: int
    average_duration_seconds: float


class Incident(BaseModel):
    service: str
    title: str
    description: str
    severity: str
    status: str
    detected_at: str
    resolved_at: str | None
    root_cause: str | None


class IncidentSearchResult(BaseModel):
    incidents: list[Incident]
    count: int


class IncidentStats(BaseModel):
    total_incidents: int
    open_incidents: int
    resolved_incidents: int
    average_resolution_time_seconds: float