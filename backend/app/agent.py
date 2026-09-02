from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from time import perf_counter
from typing import Any

from backend.app.llm.router import LLMRouter
from backend.app.mcp.client import MCPClient


logger = logging.getLogger(__name__)


@dataclass
class TraceEvent:
    timestamp: str
    event: str
    status: str
    provider: str | None = None
    tool_name: str | None = None
    duration_ms: float | None = None
    error_code: str | None = None


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _provider_name(provider: Any) -> str:
    return type(provider).__name__.removesuffix("Provider").lower()


def _safe_error_code(error: Exception) -> str:
    code = getattr(error, "code", None)
    if isinstance(code, str) and code:
        return code[:64]
    return type(error).__name__


def _contextual_question(
    question: str,
    history: list[dict[str, str]] | None,
) -> str:
    if not history:
        return question

    context_lines = [
        "The following is prior conversation context. Use it only to resolve references in the current question.",
    ]

    for turn in history[-20:]:
        role = turn.get("role", "user").upper()
        content = turn.get("content", "")
        context_lines.append(f"{role}: {content}")

    context_lines.append(f"CURRENT USER QUESTION: {question}")
    return "\n\n".join(context_lines)


class Agent:

    def __init__(self):
        self.router = LLMRouter()

    async def run(
        self,
        question: str,
        history: list[dict[str, str]] | None = None,
        trace: list[TraceEvent] | None = None,
    ) -> str:
        contextual_question = _contextual_question(question, history)

        if trace is not None:
            trace.append(
                TraceEvent(
                    timestamp=_timestamp(),
                    event="agent.request.started",
                    status="started",
                )
            )

        async with MCPClient() as mcp:
            tools = await mcp.list_tools()

            providers = self.router.get_providers()

            if not providers:
                if trace is not None:
                    trace.append(
                        TraceEvent(
                            timestamp=_timestamp(),
                            event="agent.request.failed",
                            status="error",
                        )
                    )
                raise RuntimeError(
                    "No LLM provider is configured"
                )

            last_error: Exception | None = None

            for provider in providers:
                provider_name = _provider_name(provider)
                provider_started = perf_counter()

                if trace is not None:
                    trace.append(
                        TraceEvent(
                            timestamp=_timestamp(),
                            event="llm.provider.started",
                            status="started",
                            provider=provider_name,
                        )
                    )

                try:
                    answer = await self._run_with_provider(
                        provider,
                        contextual_question,
                        tools,
                        mcp,
                        trace,
                        provider_name,
                    )

                    if trace is not None:
                        trace.append(
                            TraceEvent(
                                timestamp=_timestamp(),
                                event="llm.provider.completed",
                                status="success",
                                provider=provider_name,
                                duration_ms=round(
                                    (perf_counter() - provider_started) * 1000,
                                    2,
                                ),
                            )
                        )
                        trace.append(
                            TraceEvent(
                                timestamp=_timestamp(),
                                event="llm.provider.selected",
                                status="selected",
                                provider=provider_name,
                            )
                        )
                        trace.append(
                            TraceEvent(
                                timestamp=_timestamp(),
                                event="agent.response.completed",
                                status="success",
                            )
                        )

                    return answer
                except Exception as exc:
                    logger.warning(
                        "LLM provider %s failed with %s",
                        provider_name,
                        type(exc).__name__,
                    )

                    if trace is not None:
                        trace.append(
                            TraceEvent(
                                timestamp=_timestamp(),
                                event="llm.provider.completed",
                                status="error",
                                provider=provider_name,
                                duration_ms=round(
                                    (perf_counter() - provider_started) * 1000,
                                    2,
                                ),
                                error_code=_safe_error_code(exc),
                            )
                        )

                    last_error = exc
                    continue

            if trace is not None:
                trace.append(
                    TraceEvent(
                        timestamp=_timestamp(),
                        event="agent.request.failed",
                        status="error",
                    )
                )

            raise RuntimeError(
                "All configured LLM providers failed"
            ) from last_error

    async def _run_with_provider(
        self,
        provider: Any,
        question: str,
        tools: list[Any],
        mcp: MCPClient,
        trace: list[TraceEvent] | None,
        provider_name: str,
    ) -> str:
        response = await provider.generate(
            question,
            tools,
        )

        while response.tool_calls:
            for call in response.tool_calls:
                tool_started = perf_counter()

                if trace is not None:
                    trace.append(
                        TraceEvent(
                            timestamp=_timestamp(),
                            event="mcp.tool.started",
                            status="started",
                            provider=provider_name,
                            tool_name=call.name,
                        )
                    )

                try:
                    result = await mcp.call_tool(
                        call.name,
                        call.arguments,
                    )
                except Exception:
                    if trace is not None:
                        trace.append(
                            TraceEvent(
                                timestamp=_timestamp(),
                                event="mcp.tool.completed",
                                status="error",
                                provider=provider_name,
                                tool_name=call.name,
                                duration_ms=round(
                                    (perf_counter() - tool_started) * 1000,
                                    2,
                                ),
                                error_code="tool_invocation_failed",
                            )
                        )
                    raise

                if trace is not None:
                    tool_status = "error" if getattr(result, "is_error", False) else "success"
                    trace.append(
                        TraceEvent(
                            timestamp=_timestamp(),
                            event="mcp.tool.completed",
                            status=tool_status,
                            provider=provider_name,
                            tool_name=call.name,
                            duration_ms=round(
                                (perf_counter() - tool_started) * 1000,
                                2,
                            ),
                        )
                    )

                response = await provider.generate_with_result(
                    question,
                    response,
                    call.name,
                    result,
                    tools,
                )

        return response.text or ""
