from typing import Any

from google import genai
from google.genai import types

from backend.app.config import GEMINI_API_KEY
from backend.app.llm.base import LLMResponse, ToolCall


MODEL_NAME = "gemini-3.5-flash"


class GeminiProvider:

    def __init__(self):
        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    def _tools(self, tools: list[Any]):
        declarations = []

        for tool in tools:
            declarations.append(
                types.FunctionDeclaration(
                    name=tool.name,
                    description=tool.description or "",
                    parameters=tool.input_schema,
                )
            )

        return [
            types.Tool(
                function_declarations=declarations
            )
        ]

    def _response(self, response: Any) -> LLMResponse:
        parts = response.candidates[0].content.parts
        text_parts = []
        tool_calls = []

        for part in parts:
            if getattr(part, "text", None):
                text_parts.append(part.text)

            function_call = getattr(part, "function_call", None)
            if function_call is not None:
                tool_calls.append(
                    ToolCall(
                        name=function_call.name,
                        arguments=dict(function_call.args or {}),
                        call_id=getattr(function_call, "id", "") or "",
                    )
                )

        return LLMResponse(
            text="".join(text_parts) or None,
            tool_calls=tool_calls,
            raw=response,
        )

    def _tool_result_payload(self, tool_result: Any) -> Any:
        raw_result = getattr(tool_result, "raw", None)
        if raw_result is not None:
            return raw_result

        structured_content = getattr(tool_result, "structuredContent", None)
        if structured_content is not None:
            return structured_content

        content = getattr(tool_result, "content", None)
        if content is not None:
            return [
                getattr(item, "text", str(item))
                for item in content
            ]

        return str(tool_result)

    async def generate(
        self,
        question: str,
        tools: list[Any],
    ) -> LLMResponse:
        response = self.client.models.generate_content(
            model=MODEL_NAME,
            contents=question,
            config=types.GenerateContentConfig(
                tools=self._tools(tools)
            ),
        )
        return self._response(response)

    async def generate_with_result(
        self,
        question: str,
        response: Any,
        tool_name: str,
        tool_result: Any,
        tools: list[Any],
    ) -> LLMResponse:
        response_result = self.client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                question,
                response.raw.candidates[0].content,
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_function_response(
                            name=tool_name,
                            response={
                                "result": self._tool_result_payload(tool_result)
                            },
                        )
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                tools=self._tools(tools)
            ),
        )
        return self._response(response_result)
