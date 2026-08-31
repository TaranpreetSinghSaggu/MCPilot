import pytest

from backend.app.agent import Agent


@pytest.mark.anyio
async def test_agent_answers_repository_question():
    agent = Agent()

    answer = await agent.run(
        "Which repositories use Python?"
    )

    assert answer
    assert isinstance(answer, str)