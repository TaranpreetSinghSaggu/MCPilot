from backend.app.config import GITHUB_TOKEN
from backend.app.integrations.github.adapter import GitHubAdapter
from backend.app.integrations.github.client import GitHubClient
from backend.app.mcp.schemas import (
    GitHubIssuesResult,
    GitHubPullRequestsResult,
    GitHubRepository,
)


async def get_github_repository(
    owner: str,
    repository: str,
) -> GitHubRepository:
    async with GitHubClient(token=GITHUB_TOKEN) as client:
        adapter = GitHubAdapter(client)

        result = await adapter.get_repository(
            owner=owner,
            repository=repository,
        )

        return GitHubRepository(**result)


async def get_github_issues(
    owner: str,
    repository: str,
    state: str = "open",
    per_page: int = 30,
) -> GitHubIssuesResult:
    async with GitHubClient(token=GITHUB_TOKEN) as client:
        adapter = GitHubAdapter(client)

        issues = await adapter.get_issues(
            owner=owner,
            repository=repository,
            state=state,
            per_page=per_page,
        )

        return GitHubIssuesResult(
            issues=issues,
            count=len(issues),
        )


async def get_github_pull_requests(
    owner: str,
    repository: str,
    state: str = "open",
    per_page: int = 30,
) -> GitHubPullRequestsResult:
    async with GitHubClient(token=GITHUB_TOKEN) as client:
        adapter = GitHubAdapter(client)

        pull_requests = await adapter.get_pull_requests(
            owner=owner,
            repository=repository,
            state=state,
            per_page=per_page,
        )

        return GitHubPullRequestsResult(
            pull_requests=pull_requests,
            count=len(pull_requests),
        )