import pytest

from backend.app.mcp.client import MCPClient


@pytest.mark.anyio
async def test_mcp_client_lists_tools():
    async with MCPClient() as client:
        tools = await client.list_tools()

        tool_names = {
            tool.name
            for tool in tools
        }

        expected_tools = {
            "search_repositories",
            "search_issues",
            "search_builds",
            "get_slowest_builds",
            "search_deployments",
            "get_deployment_stats",
            "search_incidents",
            "get_incident_stats",
            "github_get_repository",
            "github_get_issues",
            "github_get_pull_requests",
        }

        assert tool_names == expected_tools


@pytest.mark.anyio
async def test_mcp_client_calls_tool():
    async with MCPClient() as client:
        result = await client.call_tool(
            "search_repositories",
            {},
        )

        assert result is not None