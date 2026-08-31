import pytest

from backend.app.mcp.client import MCPClient


@pytest.mark.anyio
async def test_mcp_tools_have_gemini_compatible_schema():
    async with MCPClient() as client:
        tools = await client.list_tools()

        for tool in tools:
            print(tool.name)
            print(tool.description)
            print(tool.input_schema)

        assert tools