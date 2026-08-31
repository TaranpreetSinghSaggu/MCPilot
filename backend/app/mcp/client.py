from typing import Any

from mcp import Client


MCP_SERVER_URL = "http://localhost:8001/mcp"


class MCPClient:
    def __init__(self, server_url: str = MCP_SERVER_URL):
        self.client = Client(server_url)
        self.session = None

    async def connect(self):
        await self.client.__aenter__()
        self.session = self.client

    async def close(self):
        await self.client.__aexit__(None, None, None)
        self.session = None

    async def list_tools(self) -> list[Any]:
        if self.session is None:
            raise RuntimeError("MCP client is not connected")

        result = await self.session.list_tools()
        return result.tools

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ):
        if self.session is None:
            raise RuntimeError("MCP client is not connected")

        return await self.session.call_tool(
            name,
            arguments or {},
        )

# as per current versioning
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        await self.close()