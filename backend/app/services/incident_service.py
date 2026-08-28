from sqlalchemy.orm import Session

from backend.app.models import Incident, Service


def search_incidents(
    session: Session,
    service_name: str | None = None,
    severity: str | None = None,
    status: str | None = None,
) -> list[Incident]:

    query = session.query(Incident)

    if service_name:
        query = query.join(Service).filter(
            Service.name == service_name
        )

    if severity:
        query = query.filter(
            Incident.severity == severity
        )

    if status:
        query = query.filter(
            Incident.status == status
        )

    return query.order_by(
        Incident.detected_at.desc()
    ).all()


def get_incident_stats(
    session: Session,
    service_name: str | None = None,
) -> dict:

    query = session.query(Incident)

    if service_name:
        query = query.join(Service).filter(
            Service.name == service_name
        )

    total_incidents = query.count()

    open_incidents = query.filter(
        Incident.resolved_at.is_(None)
    ).count()

    resolved_incidents = query.filter(
        Incident.resolved_at.is_not(None)
    ).count()

    resolved_incidents_data = query.filter(
        Incident.resolved_at.is_not(None)
    ).all()

    resolution_times = []

    for incident in resolved_incidents_data:
        if incident.resolved_at and incident.detected_at:
            resolution_time = (
                incident.resolved_at - incident.detected_at
            ).total_seconds()

            resolution_times.append(resolution_time)

    average_resolution_time = (
        sum(resolution_times) / len(resolution_times)
        if resolution_times
        else 0.0
    )

    return {
        "total_incidents": total_incidents,
        "open_incidents": open_incidents,
        "resolved_incidents": resolved_incidents,
        "average_resolution_time_seconds": average_resolution_time,
    }