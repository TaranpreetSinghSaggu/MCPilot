from typing import Any

from google import genai
from google.genai import types

from backend.app.config import GEMINI_API_KEY


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

    async def generate(
        self,
        question: str,
        tools: list[Any],
    ):
        return self.client.models.generate_content(
            model=MODEL_NAME,
            contents=question,
            config=types.GenerateContentConfig(
                tools=self._tools(tools)
            ),
        )

    async def generate_with_result(
        self,
        question: str,
        response: Any,
        tool_name: str,
        tool_result: Any,
        tools: list[Any],
    ):
        return self.client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                question,
                response.candidates[0].content,
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_function_response(
                            name=tool_name,
                            response={
                                "result": tool_result
                            },
                        )
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                tools=self._tools(tools)
            ),
        )