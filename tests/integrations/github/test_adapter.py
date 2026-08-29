import pytest

from backend.app.integrations.github.adapter import GitHubAdapter


class FakeGitHubClient:

    async def get(self, path, params=None):
        if path == "/repos/test-owner/test-repo":
            return {
                "name": "test-repo",
                "full_name": "test-owner/test-repo",
                "description": "Test repository",
                "language": "Python",
                "visibility": "private",
                "default_branch": "main",
                "html_url": "https://github.com/test-owner/test-repo",
            }

        if path == "/repos/test-owner/test-repo/issues":
            return [
                {
                    "number": 1,
                    "title": "Bug report",
                    "state": "open",
                    "html_url": "https://github.com/test-owner/test-repo/issues/1",
                    "user": {"login": "alice"},
                    "created_at": "2026-08-29T10:00:00Z",
                    "updated_at": "2026-08-29T11:00:00Z",
                },
                {
                    "number": 2,
                    "title": "Fix PR",
                    "state": "open",
                    "html_url": "https://github.com/test-owner/test-repo/pull/2",
                    "user": {"login": "bob"},
                    "created_at": "2026-08-29T10:00:00Z",
                    "updated_at": "2026-08-29T11:00:00Z",
                    "pull_request": {},
                },
            ]

        if path == "/repos/test-owner/test-repo/pulls":
            return [
                {
                    "number": 3,
                    "title": "Add feature",
                    "state": "open",
                    "html_url": "https://github.com/test-owner/test-repo/pull/3",
                    "user": {"login": "charlie"},
                    "created_at": "2026-08-29T12:00:00Z",
                    "updated_at": "2026-08-29T13:00:00Z",
                }
            ]

        raise AssertionError(f"Unexpected path: {path}")


@pytest.mark.anyio
async def test_get_repository():
    adapter = GitHubAdapter(FakeGitHubClient())

    result = await adapter.get_repository(
        "test-owner",
        "test-repo",
    )

    assert result["name"] == "test-repo"
    assert result["full_name"] == "test-owner/test-repo"
    assert result["language"] == "Python"
    assert result["visibility"] == "private"
    assert result["default_branch"] == "main"


@pytest.mark.anyio
async def test_get_issues_excludes_pull_requests():
    adapter = GitHubAdapter(FakeGitHubClient())

    result = await adapter.get_issues(
        "test-owner",
        "test-repo",
    )

    assert len(result) == 1
    assert result[0]["number"] == 1
    assert result[0]["title"] == "Bug report"
    assert result[0]["user"] == "alice"


@pytest.mark.anyio
async def test_get_pull_requests():
    adapter = GitHubAdapter(FakeGitHubClient())

    result = await adapter.get_pull_requests(
        "test-owner",
        "test-repo",
    )

    assert len(result) == 1
    assert result[0]["number"] == 3
    assert result[0]["title"] == "Add feature"
    assert result[0]["user"] == "charlie"