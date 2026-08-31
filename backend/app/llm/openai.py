from json import loads
from typing import Any

from openai import AsyncOpenAI

from backend.app.config import OPENAI_API_KEY
from backend.app.llm.base import LLMResponse, ToolCall


MODEL_NAME = "gpt-4o-mini"


class OpenAIProvider:

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=OPENAI_API_KEY
        )

    def _tools(self, tools: list[Any]):
        result = []

        for tool in tools:
            result.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.input_schema,
                    },
                }
            )

        return result

    def _response(self, response: Any) -> LLMResponse:
        message = response.choices[0].message

        tool_calls = []

        for call in message.tool_calls or []:
            tool_calls.append(
                ToolCall(
                    name=call.function.name,
                    arguments=loads(call.function.arguments),
                    call_id=call.id,
                )
            )

        return LLMResponse(
            text=message.content,
            tool_calls=tool_calls,
            raw=response,
        )

    async def generate(
        self,
        question: str,
        tools: list[Any],
    ) -> LLMResponse:

        response = await self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
            tools=self._tools(tools),
        )

        return self._response(response)

    async def generate_with_result(
        self,
        question: str,
        response: LLMResponse,
        tool_name: str,
        tool_result: Any,
        tools: list[Any],
    ) -> LLMResponse:

        original_message = response.raw.choices[0].message

        messages = [
            {
                "role": "user",
                "content": question,
            },
            {
                "role": "assistant",
                "content": original_message.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in original_message.tool_calls
                ],
            },
        ]

        tool_call = next(
            call
            for call in original_message.tool_calls
            if call.function.name == tool_name
        )

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result),
            }
        )

        result = await self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=self._tools(tools),
        )

        return self._response(result)