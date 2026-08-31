from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]
    call_id: str


@dataclass
class LLMResponse:
    text: str | None
    tool_calls: list[ToolCall]
    raw: Any


class LLMProvider(Protocol):
    async def generate(
        self,
        question: str,
        tools: list[Any],
    ) -> LLMResponse:
        ...

    async def generate_with_result(
        self,
        question: str,
        response: LLMResponse,
        tool_name: str,
        tool_result: Any,
        tools: list[Any],
    ) -> LLMResponse:
        ...