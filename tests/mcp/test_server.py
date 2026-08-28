# import pytest

# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client


# @pytest.mark.anyio
# async def test_server_lists_tools():
#     server_params = StdioServerParameters(
#         command="python3",
#         args=["-m", "backend.app.mcp.server"],
#     )

#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()

#             result = await session.list_tools()

#             tool_names = {
#                 tool.name
#                 for tool in result.tools
#             }

#             expected_tools = {
#                 "search_repositories",
#                 "search_issues",
#                 "search_builds",
#                 "get_slowest_builds",
#                 "search_deployments",
#                 "get_deployment_stats",
#                 "search_incidents",
#                 "get_incident_stats",
#             }

#             assert tool_names == expected_tools

import json

import pytest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER_PARAMS = StdioServerParameters(
    command="python3",
    args=["-m", "backend.app.mcp.server"],
)


@pytest.mark.anyio
async def test_server_lists_tools():
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.list_tools()

            tool_names = {
                tool.name
                for tool in result.tools
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
            }

            assert tool_names == expected_tools


@pytest.mark.anyio
async def test_server_calls_search_repositories():
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "search_repositories",
                {
                    "language": "Python",
                },
            )

            assert result.is_error is False
            assert result.content

            text_content = result.content[0]

            assert text_content.type == "text"

            content = json.loads(text_content.text)

            assert content["count"] > 0
            assert len(content["repositories"]) == content["count"]

            for repository in content["repositories"]:
                assert repository["language"] == "Python"

@pytest.mark.anyio
async def test_server_calls_search_incidents():
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "search_incidents",
                {
                    "severity": "critical",
                },
            )

            assert result.is_error is False
            assert result.content

            text_content = result.content[0]

            assert text_content.type == "text"

            content = json.loads(text_content.text)

            assert content["count"] > 0
            assert len(content["incidents"]) == content["count"]

            for incident in content["incidents"]:
                assert incident["severity"] == "critical"

@pytest.mark.anyio
async def test_server_handles_tool_error():
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "search_repositories",
                {
                    "language": "__definitely_not_a_real_language__",
                },
            )

            assert result.is_error is False
            assert result.content

            text_content = result.content[0]
            assert text_content.type == "text"

            content = json.loads(text_content.text)

            assert content["count"] == 0
            assert content["repositories"] == []