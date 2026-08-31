from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.agent import Agent


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=AgentResponse)
async def chat(request: AgentRequest):
    agent = Agent()

    answer = await agent.run(request.message)

    return AgentResponse(answer=answer)