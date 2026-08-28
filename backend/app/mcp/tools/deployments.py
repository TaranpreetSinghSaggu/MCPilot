from sqlalchemy.orm import Session

from backend.app.services.deployment_service import (
    get_deployment_stats,
    search_deployments,
)


def search_deployments_tool(
    session: Session,
    service_name: str | None = None,
    environment: str | None = None,
    status: str | None = None,
) -> dict:

    deployments = search_deployments(
        session=session,
        service_name=service_name,
        environment=environment,
        status=status,
    )

    return {
        "deployments": [
            {
                "service": deployment.service.name,
                "commit_id": deployment.commit_id,
                "environment": deployment.environment,
                "status": deployment.status,
                "version": deployment.version,
                "duration_seconds": deployment.duration_seconds,
                "deployed_by": deployment.deployer.username,
                "started_at": deployment.started_at.isoformat(),
                "completed_at": deployment.completed_at.isoformat(),
            }
            for deployment in deployments
        ],
        "count": len(deployments),
    }


def get_deployment_stats_tool(
    session: Session,
    service_name: str | None = None,
    environment: str | None = None,
) -> dict:

    stats = get_deployment_stats(
        session=session,
        service_name=service_name,
        environment=environment,
    )

    return stats