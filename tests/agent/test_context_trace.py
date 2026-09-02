from types import SimpleNamespace

import pytest

from backend.app import agent as agent_module
from backend.app.agent import Agent, TraceEvent, _contextual_question


def test_contextual_question_is_bounded_and_delimited():
    history = [
        {"role": "user", "content": f"Turn {index}"}
        for index in range(25)
    ]

    contextual = _contextual_question("Current question", history)

    assert "Turn 0" not in contextual
    assert "Turn 5" in contextual
    assert "CURRENT USER QUESTION: Current question" in contextual


@pytest.mark.anyio
async def test_agent_forwards_history_and_records_safe_provider_trace(monkeypatch):
    captured_questions: list[str] = []

    class FakeProvider:
        async def generate(self, question, tools):
            captured_questions.append(question)
            return SimpleNamespace(text="Answer", tool_calls=[])

    class FakeRouter:
        def get_providers(self):
            return [FakeProvider()]

    class FakeMCPClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

        async def list_tools(self):
            return []

    monkeypatch.setattr(agent_module, "LLMRouter", FakeRouter)
    monkeypatch.setattr(agent_module, "MCPClient", FakeMCPClient)

    trace: list[TraceEvent] = []
    answer = await Agent().run(
        "Follow up",
        history=[{"role": "user", "content": "Earlier question"}],
        trace=trace,
    )

    assert answer == "Answer"
    assert "Earlier question" in captured_questions[0]
    assert [event.event for event in trace] == [
        "agent.request.started",
        "llm.provider.started",
        "llm.provider.completed",
        "llm.provider.selected",
        "agent.response.completed",
    ]
    assert all(not hasattr(event, "arguments") for event in trace)
    assert all(not hasattr(event, "result") for event in trace)


@pytest.mark.anyio
async def test_agent_records_tool_success_without_payloads(monkeypatch):
    class FakeProvider:
        def __init__(self):
            self.calls = 0

        async def generate(self, question, tools):
            self.calls += 1
            return SimpleNamespace(
                text=None,
                tool_calls=[SimpleNamespace(name="list_builds", arguments={"secret": "hidden"})],
            )

        async def generate_with_result(self, question, response, tool_name, tool_result, tools):
            return SimpleNamespace(text="Tool answer", tool_calls=[])

    provider = FakeProvider()

    class FakeRouter:
        def get_providers(self):
            return [provider]

    class FakeMCPClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

        async def list_tools(self):
            return []

        async def call_tool(self, name, arguments):
            return SimpleNamespace(is_error=False, raw={"secret": "hidden"})

    monkeypatch.setattr(agent_module, "LLMRouter", FakeRouter)
    monkeypatch.setattr(agent_module, "MCPClient", FakeMCPClient)

    trace: list[TraceEvent] = []
    answer = await Agent().run("List builds", trace=trace)

    assert answer == "Tool answer"
    tool_events = [event for event in trace if event.event.startswith("mcp.tool")]
    assert [event.status for event in tool_events] == ["started", "success"]
    assert all("secret" not in repr(event) for event in tool_events)


@pytest.mark.anyio
async def test_agent_records_provider_failure_before_fallback(monkeypatch):
    class FailingProvider:
        async def generate(self, question, tools):
            raise RuntimeError("provider down")

    class WorkingProvider:
        async def generate(self, question, tools):
            return SimpleNamespace(text="Fallback answer", tool_calls=[])

    class FakeRouter:
        def get_providers(self):
            return [FailingProvider(), WorkingProvider()]

    class FakeMCPClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

        async def list_tools(self):
            return []

    monkeypatch.setattr(agent_module, "LLMRouter", FakeRouter)
    monkeypatch.setattr(agent_module, "MCPClient", FakeMCPClient)

    trace: list[TraceEvent] = []
    answer = await Agent().run("Try providers", trace=trace)

    assert answer == "Fallback answer"
    provider_events = [event for event in trace if event.event == "llm.provider.completed"]
    assert [event.status for event in provider_events] == ["error", "success"]
    assert provider_events[0].error_code == "RuntimeError"
    assert trace[-1].event == "agent.response.completed"
