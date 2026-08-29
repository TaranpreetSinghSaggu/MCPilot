from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import DATABASE_URL
from backend.app.mcp.tools.deployments import (
    get_deployment_stats_tool,
    search_deployments_tool,
)


engine = create_engine(DATABASE_URL)


def test_search_deployments_tool():
    with Session(engine) as session:
        result = search_deployments_tool(session)

        assert result.count == 35
        assert len(result.deployments) == 35


def test_search_failed_deployments_tool():
    with Session(engine) as session:
        result = search_deployments_tool(
            session,
            status="failed",
        )

        assert result.count > 0

        for deployment in result.deployments:
            assert deployment.status == "failed"


def test_search_production_deployments_tool():
    with Session(engine) as session:
        result = search_deployments_tool(
            session,
            environment="production",
        )

        assert result.count > 0

        for deployment in result.deployments:
            assert deployment.environment == "production"


def test_search_deployments_for_service():
    with Session(engine) as session:
        result = search_deployments_tool(
            session,
            service_name="payment-api",
        )

        assert result.count > 0

        for deployment in result.deployments:
            assert deployment.service == "payment-api"


def test_get_deployment_stats():
    with Session(engine) as session:
        result = get_deployment_stats_tool(
            session,
            service_name="payment-api",
        )

        assert result.total_deployments >= 0
        assert result.successful_deployments >= 0
        assert result.failed_deployments >= 0
        assert result.average_duration_seconds >= 0