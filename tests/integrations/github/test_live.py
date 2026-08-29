import pytest

from backend.app.config import GITHUB_TOKEN
from backend.app.integrations.github.adapter import GitHubAdapter
from backend.app.integrations.github.client import GitHubClient


@pytest.mark.anyio
async def test_live_get_repository():
    if not GITHUB_TOKEN:
        pytest.skip("GITHUB_TOKEN not configured")

    client = GitHubClient(token=GITHUB_TOKEN)
    adapter = GitHubAdapter(client)

    result = await adapter.get_repository(
        "octocat",
        "Hello-World",
    )

    assert result["name"] == "Hello-World"
    assert result["full_name"] == "octocat/Hello-World"
    assert result["html_url"]