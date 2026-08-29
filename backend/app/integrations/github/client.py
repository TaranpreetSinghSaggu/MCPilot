from typing import Any

import httpx

from backend.app.integrations.base import BaseIntegration
from backend.app.integrations.exceptions import (
    IntegrationAuthenticationError,
    IntegrationNotFoundError,
    IntegrationRateLimitError,
    IntegrationRequestError,
)


class GitHubClient(BaseIntegration):

    platform = "github"

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.github.com",
        timeout: float = 10.0,
    ) -> None:
        if not token:
            raise ValueError("GitHub token is required")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

    async def health_check(self) -> bool:
        try:
            response = await self._client.get("/rate_limit")
            response.raise_for_status()
            return True
        except httpx.HTTPError:
            return False

    async def get(
        self,
        path: str,
        **kwargs: Any,
    ) -> Any:
        try:
            response = await self._client.get(path, **kwargs)

        except httpx.TimeoutException as exc:
            raise IntegrationRequestError(
                "GitHub request timed out"
            ) from exc

        except httpx.HTTPError as exc:
            raise IntegrationRequestError(
                f"GitHub request failed: {exc}"
            ) from exc

        if response.status_code in (401, 403):
            if response.headers.get("X-RateLimit-Remaining") == "0":
                raise IntegrationRateLimitError(
                    "GitHub API rate limit exceeded"
                )

            raise IntegrationAuthenticationError(
                "GitHub authentication failed"
            )

        if response.status_code == 404:
            raise IntegrationNotFoundError(
                f"GitHub resource not found: {path}"
            )

        if response.status_code == 429:
            raise IntegrationRateLimitError(
                "GitHub API rate limit exceeded"
            )

        if response.is_error:
            raise IntegrationRequestError(
                f"GitHub API returned HTTP {response.status_code}"
            )

        return response.json()

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "GitHubClient":
        return self

    async def __aexit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        await self.close()