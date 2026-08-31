from typing import Any

from backend.app.llm.router import LLMRouter
from backend.app.mcp.client import MCPClient


class Agent:

    def __init__(self):
        self.router = LLMRouter()

    async def run(self, question: str) -> str:
        async with MCPClient() as mcp:
            tools = await mcp.list_tools()

            providers = self.router.get_providers()

            if not providers:
                raise RuntimeError(
                    "No LLM provider is configured"
                )

            last_error: Exception | None = None

            for provider in providers:
                try:
                    return await self._run_with_provider(
                        provider,
                        question,
                        tools,
                        mcp,
                    )
                except Exception as exc:
                    print(
                     f"{type(provider).__name__} failed: "
                     f"{type(exc).__name__}: {exc}"
                    )
                    last_error = exc
                    continue

            raise RuntimeError(
                "All configured LLM providers failed"
            ) from last_error

    async def _run_with_provider(
        self,
        provider: Any,
        question: str,
        tools: list[Any],
        mcp: MCPClient,
    ) -> str:
        response = await provider.generate(
            question,
            tools,
        )

        while response.tool_calls:
            for call in response.tool_calls:
                result = await mcp.call_tool(
                    call.name,
                    call.arguments,
                )

                response = await provider.generate_with_result(
                    question,
                    response,
                    call.name,
                    result,
                    tools,
                )

        return response.text