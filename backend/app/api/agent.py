from fastapi import APIRouter
from dataclasses import asdict
from typing import Literal

from pydantic import BaseModel, Field

from backend.app.agent import Agent, TraceEvent


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


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
