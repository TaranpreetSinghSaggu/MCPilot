from dataclasses import asdict
import logging
from typing import Literal

import anyio
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.agent import Agent, TraceEvent
from backend.app.config import MCP_SERVER_URL
from backend.app.mcp.client import MCPClient


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)

MCP_READINESS_TIMEOUT_SECONDS = 120.0
MCP_READINESS_INITIAL_DELAY_SECONDS = 1.0
MCP_READINESS_MAX_DELAY_SECONDS = 15.0

MCP_WAKE_URL = f"{MCP_SERVER_URL.rsplit('/mcp', 1)[0]}/health"


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AgentRequest(BaseModel):
    message: str
    history: list[ChatTurn] = Field(default_factory=list, max_length=20)


class TraceEventResponse(BaseModel):
    timestamp: str
    event: str
    status: str
    provider: str | None = None
    tool_name: str | None = None
    duration_ms: float | None = None
    error_code: str | None = None


class AgentResponse(BaseModel):
    answer: str
    trace: list[TraceEventResponse] = Field(default_factory=list)


class MCPReadinessResponse(BaseModel):
    status: Literal["ready"]
    service: Literal["mcp"]


async def _retry_mcp_readiness() -> None:
    delay = MCP_READINESS_INITIAL_DELAY_SECONDS

    async with httpx.AsyncClient(timeout=15.0) as http:
        while True:
            try:
                wake_response = await http.get(MCP_WAKE_URL)
                wake_response.raise_for_status()

                async with MCPClient() as client:
                    await client.list_tools()

                return

            except Exception as exc:
                logger.warning(
                    "MCP readiness attempt failed with %s",
                    type(exc).__name__,
                )
                await anyio.sleep(delay)
                delay = min(delay * 2, MCP_READINESS_MAX_DELAY_SECONDS)


@router.get("/readiness", response_model=MCPReadinessResponse)
async def readiness():
    try:
        with anyio.fail_after(MCP_READINESS_TIMEOUT_SECONDS):
            await _retry_mcp_readiness()
    except TimeoutError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "MCP service did not become ready within 2 minutes. "
                "It may still be waking up. Please retry readiness."
            ),
        ) from exc

    return MCPReadinessResponse(status="ready", service="mcp")


@router.post("/chat", response_model=AgentResponse)
async def chat(request: AgentRequest):
    agent = Agent()
    trace: list[TraceEvent] = []
    history = [turn.model_dump() for turn in request.history]

    answer = await agent.run(
        request.message,
        history=history,
        trace=trace,
    )

    return AgentResponse(
        answer=answer,
        trace=[TraceEventResponse(**asdict(event)) for event in trace],
    )