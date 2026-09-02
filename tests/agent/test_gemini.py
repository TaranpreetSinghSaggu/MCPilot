from types import SimpleNamespace

from backend.app.llm.gemini import GeminiProvider
from backend.app.llm.base import LLMResponse


def test_gemini_normalizes_text_response():
    response = SimpleNamespace(
        candidates=[
            SimpleNamespace(
                content=SimpleNamespace(
                    parts=[SimpleNamespace(text="Hello")]
                )
            )
        ]
    )

    normalized = GeminiProvider.__new__(GeminiProvider)._response(response)

    assert isinstance(normalized, LLMResponse)
    assert normalized.text == "Hello"
    assert normalized.tool_calls == []
    assert normalized.raw is response


def test_gemini_normalizes_tool_call_response():
    function_call = SimpleNamespace(
        name="search_repositories",
        args={"language": "Python"},
    )
    response = SimpleNamespace(
        candidates=[
            SimpleNamespace(
                content=SimpleNamespace(
                    parts=[SimpleNamespace(function_call=function_call)]
                )
            )
        ]
    )

    normalized = GeminiProvider.__new__(GeminiProvider)._response(response)

    assert len(normalized.tool_calls) == 1
    assert normalized.tool_calls[0].name == "search_repositories"
    assert normalized.tool_calls[0].arguments == {"language": "Python"}
    assert normalized.tool_calls[0].call_id == ""
