import httpx
import pytest

from backend.app.integrations.exceptions import (
    IntegrationAuthenticationError,
    IntegrationNotFoundError,
    IntegrationRateLimitError,
    IntegrationRequestError,
)
from backend.app.integrations.github.client import GitHubClient


@pytest.mark.anyio
async def test_github_get_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/repos/test-owner/test-repo"
        return httpx.Response(
            200,
            json={
                "name": "test-repo",
            },
        )

    client = GitHubClient(token="test-token")
    await client._client.aclose()
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    try:
        result = await client.get(
            "/repos/test-owner/test-repo"
        )

        assert result["name"] == "test-repo"
    finally:
        await client.close()


@pytest.mark.anyio
async def test_github_authentication_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401)

    client = GitHubClient(token="test-token")
    await client._client.aclose()
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    try:
        with pytest.raises(IntegrationAuthenticationError):
            await client.get("/user")
    finally:
        await client.close()


@pytest.mark.anyio
async def test_github_not_found_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    client = GitHubClient(token="test-token")
    await client._client.aclose()
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    try:
        with pytest.raises(IntegrationNotFoundError):
            await client.get("/repos/missing/repo")
    finally:
        await client.close()


@pytest.mark.anyio
async def test_github_rate_limit_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403,
            headers={"X-RateLimit-Remaining": "0"},
        )

    client = GitHubClient(token="test-token")
    await client._client.aclose()
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    try:
        with pytest.raises(IntegrationRateLimitError):
            await client.get("/rate_limit")
    finally:
        await client.close()


@pytest.mark.anyio
async def test_github_request_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    client = GitHubClient(token="test-token")
    await client._client.aclose()
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    try:
        with pytest.raises(IntegrationRequestError):
            await client.get("/server-error")
    finally:
        await client.close()