from typing import Any

from backend.app.integrations.github.client import GitHubClient


class GitHubAdapter:

    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    async def get_repository(
        self,
        owner: str,
        repository: str,
    ) -> dict[str, Any]:
        data = await self.client.get(
            f"/repos/{owner}/{repository}"
        )

        return {
            "name": data["name"],
            "full_name": data["full_name"],
            "description": data.get("description"),
            "language": data.get("language"),
            "visibility": data.get("visibility"),
            "default_branch": data.get("default_branch"),
            "html_url": data.get("html_url"),
        }

    async def get_issues(
        self,
        owner: str,
        repository: str,
        state: str = "open",
        per_page: int = 30,
    ) -> list[dict[str, Any]]:
        data = await self.client.get(
            f"/repos/{owner}/{repository}/issues",
            params={
                "state": state,
                "per_page": per_page,
            },
        )

        return [
            {
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "html_url": issue["html_url"],
                "user": (
                    issue["user"]["login"]
                    if issue.get("user")
                    else None
                ),
                "created_at": issue.get("created_at"),
                "updated_at": issue.get("updated_at"),
            }
            for issue in data
            if "pull_request" not in issue
        ]

    async def get_pull_requests(
        self,
        owner: str,
        repository: str,
        state: str = "open",
        per_page: int = 30,
    ) -> list[dict[str, Any]]:
        data = await self.client.get(
            f"/repos/{owner}/{repository}/pulls",
            params={
                "state": state,
                "per_page": per_page,
            },
        )

        return [
            {
                "number": pull_request["number"],
                "title": pull_request["title"],
                "state": pull_request["state"],
                "html_url": pull_request["html_url"],
                "user": (
                    pull_request["user"]["login"]
                    if pull_request.get("user")
                    else None
                ),
                "created_at": pull_request.get("created_at"),
                "updated_at": pull_request.get("updated_at"),
            }
            for pull_request in data
        ]