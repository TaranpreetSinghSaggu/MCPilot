from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models import Deployment, Service


def search_deployments(
    session: Session,
    service_name: str | None = None,
    environment: str | None = None,
    status: str | None = None,
) -> list[Deployment]:

    query = session.query(Deployment)

    if service_name:
        query = query.join(Service).filter(
            Service.name == service_name
        )

    if environment:
        query = query.filter(
            Deployment.environment == environment
        )

    if status:
        query = query.filter(
            Deployment.status == status
        )

    return query.order_by(
        Deployment.started_at.desc()
    ).all()


def get_deployment_stats(
    session: Session,
    service_name: str | None = None,
    environment: str | None = None,
) -> dict:

    query = session.query(Deployment)

    if service_name:
        query = query.join(Service).filter(
            Service.name == service_name
        )

    if environment:
        query = query.filter(
            Deployment.environment == environment
        )

    total_deployments = query.count()

    successful_deployments = query.filter(
        Deployment.status == "success"
    ).count()

    failed_deployments = query.filter(
        Deployment.status == "failed"
    ).count()

    average_duration = query.with_entities(
        func.avg(Deployment.duration_seconds)
    ).scalar()

    return {
        "total_deployments": total_deployments,
        "successful_deployments": successful_deployments,
        "failed_deployments": failed_deployments,
        "average_duration_seconds": (
            float(average_duration)
            if average_duration is not None
            else 0.0
        ),
    }