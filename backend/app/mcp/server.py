from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mcp.server.mcpserver import MCPServer

from backend.app.config import DATABASE_URL
from backend.app.mcp.tools.builds import (
    get_slowest_builds_tool,
    search_builds_tool,
)
from backend.app.mcp.tools.deployments import (
    get_deployment_stats_tool,
    search_deployments_tool,
)
from backend.app.mcp.tools.incidents import (
    get_incident_stats_tool,
    search_incidents_tool,
)
from backend.app.mcp.tools.issues import search_issues_tool
from backend.app.mcp.tools.repositories import search_repositories

from backend.app.mcp.tools.github import (
    get_github_issues,
    get_github_pull_requests,
    get_github_repository,
)


engine = create_engine(DATABASE_URL)

mcp = MCPServer(
    name="MCPilot",
    description="MCP server for software engineering and DevOps intelligence.",
    version="0.1.0",
)


@mcp.tool(
    name="search_repositories",
    description="Search repositories using optional language, team, and visibility filters.",
)
def search_repositories_mcp(
    language: str | None = None,
    team: str | None = None,
    visibility: str | None = None,
) -> dict:
    with Session(engine) as session:
        return search_repositories(
            session=session,
            language=language,
            team=team,
            visibility=visibility,
        )


@mcp.tool(
    name="search_issues",
    description="Search issues using optional repository, priority, status, and assignee filters.",
)
def search_issues_mcp(
    repository_name: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    assignee_username: str | None = None,
) -> dict:
    with Session(engine) as session:
        return search_issues_tool(
            session=session,
            repository_name=repository_name,
            priority=priority,
            status=status,
            assignee_username=assignee_username,
        )


@mcp.tool(
    name="search_builds",
    description="Search build runs using optional repository and status filters.",
)
def search_builds_mcp(
    repository_name: str | None = None,
    status: str | None = None,
) -> dict:
    with Session(engine) as session:
        return search_builds_tool(
            session=session,
            repository_name=repository_name,
            status=status,
        )


@mcp.tool(
    name="get_slowest_builds",
    description="Return the slowest build runs, optionally limited to a repository.",
)
def get_slowest_builds_mcp(
    repository_name: str | None = None,
    limit: int = 5,
) -> dict:
    with Session(engine) as session:
        return get_slowest_builds_tool(
            session=session,
            repository_name=repository_name,
            limit=limit,
        )


@mcp.tool(
    name="search_deployments",
    description="Search deployments using optional service, environment, and status filters.",
)
def search_deployments_mcp(
    service_name: str | None = None,
    environment: str | None = None,
    status: str | None = None,
) -> dict:
    with Session(engine) as session:
        return search_deployments_tool(
            session=session,
            service_name=service_name,
            environment=environment,
            status=status,
        )


@mcp.tool(
    name="get_deployment_stats",
    description="Return deployment statistics, optionally filtered by service and environment.",
)
def get_deployment_stats_mcp(
    service_name: str | None = None,
    environment: str | None = None,
) -> dict:
    with Session(engine) as session:
        return get_deployment_stats_tool(
            session=session,
            service_name=service_name,
            environment=environment,
        )


@mcp.tool(
    name="search_incidents",
    description="Search incidents using optional service, severity, and status filters.",
)
def search_incidents_mcp(
    service_name: str | None = None,
    severity: str | None = None,
    status: str | None = None,
) -> dict:
    with Session(engine) as session:
        return search_incidents_tool(
            session=session,
            service_name=service_name,
            severity=severity,
            status=status,
        )


@mcp.tool(
    name="get_incident_stats",
    description="Return incident statistics, optionally filtered by service.",
)
def get_incident_stats_mcp(
    service_name: str | None = None,
) -> dict:
    with Session(engine) as session:
        return get_incident_stats_tool(
            session=session,
            service_name=service_name,
        )

@mcp.tool(
    name="github_get_repository",
    description="Get repository information from GitHub using the repository owner and name.",
)
async def github_get_repository_mcp(
    owner: str,
    repository: str,
):
    return await get_github_repository(
        owner=owner,
        repository=repository,
    )


@mcp.tool(
    name="github_get_issues",
    description="Get issues from a GitHub repository, optionally filtered by state.",
)
async def github_get_issues_mcp(
    owner: str,
    repository: str,
    state: str = "open",
    per_page: int = 30,
):
    return await get_github_issues(
        owner=owner,
        repository=repository,
        state=state,
        per_page=per_page,
    )


@mcp.tool(
    name="github_get_pull_requests",
    description="Get pull requests from a GitHub repository, optionally filtered by state.",
)
async def github_get_pull_requests_mcp(
    owner: str,
    repository: str,
    state: str = "open",
    per_page: int = 30,
):
    return await get_github_pull_requests(
        owner=owner,
        repository=repository,
        state=state,
        per_page=per_page,
    )



if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        stateless_http=True,
        json_response=True,
        port=8001,
    )