from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.services.deployment_service import (
    get_deployment_stats,
    search_deployments,
)


router = APIRouter(
    prefix="/deployments",
    tags=["deployments"],
)


@router.get("")
def get_deployments(
    service_name: str | None = None,
    environment: str | None = None,
    status: str | None = None,
    session: Session = Depends(get_db),
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


@router.get("/stats")
def get_deployment_statistics(
    service_name: str | None = None,
    environment: str | None = None,
    session: Session = Depends(get_db),
) -> dict:
    return get_deployment_stats(
        session=session,
        service_name=service_name,
        environment=environment,
    )