from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import DATABASE_URL
from backend.app.services.deployment_service import (
    get_deployment_stats,
    search_deployments,
)


engine = create_engine(DATABASE_URL)


def test_search_deployments():
    with Session(engine) as session:
        deployments = search_deployments(session)

        assert len(deployments) == 35


def test_search_failed_deployments():
    with Session(engine) as session:
        deployments = search_deployments(
            session,
            status="failed",
        )

        assert deployments

        for deployment in deployments:
            assert deployment.status == "failed"


def test_search_production_deployments():
    with Session(engine) as session:
        deployments = search_deployments(
            session,
            environment="production",
        )

        assert deployments

        for deployment in deployments:
            assert deployment.environment == "production"


def test_search_deployments_for_service():
    with Session(engine) as session:
        deployments = search_deployments(
            session,
            service_name="payment-api",
        )

        assert deployments

        for deployment in deployments:
            assert deployment.service.name == "payment-api"


def test_get_deployment_stats():
    with Session(engine) as session:
        stats = get_deployment_stats(
            session,
            service_name="payment-service",
            environment="production",
        )

        assert stats["total_deployments"] >= 0
        assert stats["successful_deployments"] >= 0
        assert stats["failed_deployments"] >= 0
        assert stats["average_duration_seconds"] >= 0