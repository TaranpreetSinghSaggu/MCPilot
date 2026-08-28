from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import DATABASE_URL
from backend.app.mcp.tools.incidents import (
    get_incident_stats_tool,
    search_incidents_tool,
)


engine = create_engine(DATABASE_URL)


def test_search_incidents_tool():
    with Session(engine) as session:
        result = search_incidents_tool(session)

        assert result["count"] == 20
        assert len(result["incidents"]) == 20


def test_search_critical_incidents_tool():
    with Session(engine) as session:
        result = search_incidents_tool(
            session,
            severity="critical",
        )

        assert result["count"] > 0

        for incident in result["incidents"]:
            assert incident["severity"] == "critical"


def test_search_open_incidents_tool():
    with Session(engine) as session:
        result = search_incidents_tool(
            session,
            status="open",
        )

        assert result["count"] > 0

        for incident in result["incidents"]:
            assert incident["status"] == "open"


def test_search_incidents_for_service():
    with Session(engine) as session:
        result = search_incidents_tool(
            session,
            service_name="payment-api",
        )

        assert result["count"] > 0

        for incident in result["incidents"]:
            assert incident["service"] == "payment-api"


def test_get_incident_stats():
    with Session(engine) as session:
        result = get_incident_stats_tool(
            session,
            service_name="payment-api",
        )

        assert result["total_incidents"] >= 0
        assert result["open_incidents"] >= 0
        assert result["resolved_incidents"] >= 0
        assert result["average_resolution_time_seconds"] >= 0