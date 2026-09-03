import pytest
from fastapi import HTTPException

from backend.app.api import agent as agent_api


class FakeMCPClient:
    instances = []
    enter_failures_before_success = 0
    failures_before_success = 0

    def __init__(self):
        self.list_tools_calls = 0
        self.closed = False
        type(self).instances.append(self)

    async def __aenter__(self):
        if type(self).enter_failures_before_success > 0:
            type(self).enter_failures_before_success -= 1
            raise RuntimeError("MCP handshake is still in progress")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.closed = True

    async def list_tools(self):
        self.list_tools_calls += 1
        if type(self).failures_before_success > 0:
            type(self).failures_before_success -= 1
            raise RuntimeError("MCP is waking up")
        return []


@pytest.mark.anyio
async def test_readiness_verifies_tools_and_closes_the_client(monkeypatch):
    FakeMCPClient.instances = []
    FakeMCPClient.enter_failures_before_success = 0
    FakeMCPClient.failures_before_success = 0
    monkeypatch.setattr(agent_api, "MCPClient", FakeMCPClient)
    monkeypatch.setattr(agent_api, "MCP_READINESS_TIMEOUT_SECONDS", 1.0)

    response = await agent_api.readiness()

    assert response.status == "ready"
    assert response.service == "mcp"
    assert len(FakeMCPClient.instances) == 1
    assert FakeMCPClient.instances[0].list_tools_calls == 1
    assert FakeMCPClient.instances[0].closed is True


@pytest.mark.anyio
async def test_readiness_retries_transient_mcp_failure(monkeypatch):
    FakeMCPClient.instances = []
    FakeMCPClient.enter_failures_before_success = 0
    FakeMCPClient.failures_before_success = 2
    monkeypatch.setattr(agent_api, "MCPClient", FakeMCPClient)
    monkeypatch.setattr(agent_api, "MCP_READINESS_TIMEOUT_SECONDS", 1.0)
    monkeypatch.setattr(agent_api, "MCP_READINESS_INITIAL_DELAY_SECONDS", 0.001)
    monkeypatch.setattr(agent_api, "MCP_READINESS_MAX_DELAY_SECONDS", 0.001)

    response = await agent_api.readiness()

    assert response.status == "ready"
    assert len(FakeMCPClient.instances) == 3
    assert all(client.closed for client in FakeMCPClient.instances)


@pytest.mark.anyio
async def test_readiness_retries_handshake_failure(monkeypatch):
    FakeMCPClient.instances = []
    FakeMCPClient.enter_failures_before_success = 2
    FakeMCPClient.failures_before_success = 0
    monkeypatch.setattr(agent_api, "MCPClient", FakeMCPClient)
    monkeypatch.setattr(agent_api, "MCP_READINESS_TIMEOUT_SECONDS", 1.0)
    monkeypatch.setattr(agent_api, "MCP_READINESS_INITIAL_DELAY_SECONDS", 0.001)
    monkeypatch.setattr(agent_api, "MCP_READINESS_MAX_DELAY_SECONDS", 0.001)

    response = await agent_api.readiness()

    assert response.status == "ready"
    assert len(FakeMCPClient.instances) == 3
    assert FakeMCPClient.instances[-1].closed is True


@pytest.mark.anyio
async def test_readiness_returns_503_after_the_deadline(monkeypatch):
    FakeMCPClient.instances = []
    FakeMCPClient.enter_failures_before_success = 0
    FakeMCPClient.failures_before_success = 10_000
    monkeypatch.setattr(agent_api, "MCPClient", FakeMCPClient)
    monkeypatch.setattr(agent_api, "MCP_READINESS_TIMEOUT_SECONDS", 0.02)
    monkeypatch.setattr(agent_api, "MCP_READINESS_INITIAL_DELAY_SECONDS", 0.01)
    monkeypatch.setattr(agent_api, "MCP_READINESS_MAX_DELAY_SECONDS", 0.01)

    with pytest.raises(HTTPException) as error:
        await agent_api.readiness()

    assert error.value.status_code == 503
    assert "did not become ready within 2 minutes" in error.value.detail
    assert FakeMCPClient.instances
    assert all(client.closed for client in FakeMCPClient.instances)
