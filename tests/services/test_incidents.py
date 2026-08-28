from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import DATABASE_URL
from backend.app.services.incident_service import (
    get_incident_stats,
    search_incidents,
)


engine = create_engine(DATABASE_URL)


def test_search_incidents():
    with Session(engine) as session:
        incidents = search_incidents(session)

        assert len(incidents) == 20


def test_search_critical_incidents():
    with Session(engine) as session:
        incidents = search_incidents(
            session,
            severity="critical",
        )

        assert incidents

        for incident in incidents:
            assert incident.severity == "critical"


def test_search_open_incidents():
    with Session(engine) as session:
        incidents = search_incidents(
            session,
            status="open",
        )

        assert incidents

        for incident in incidents:
            assert incident.status == "open"


def test_search_incidents_for_service():
    with Session(engine) as session:
        incidents = search_incidents(
            session,
            service_name="payment-api",
        )

        assert incidents

        for incident in incidents:
            assert incident.service.name == "payment-api"


def test_get_incident_stats():
    with Session(engine) as session:
        stats = get_incident_stats(
            session,
            service_name="payment-api",
        )

        assert stats["total_incidents"] >= 0
        assert stats["open_incidents"] >= 0
        assert stats["resolved_incidents"] >= 0
        assert stats["average_resolution_time_seconds"] >= 0