from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.services.incident_service import (
    get_incident_stats,
    search_incidents,
)


router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)


@router.get("")
def get_incidents(
    service_name: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    session: Session = Depends(get_db),
) -> dict:
    incidents = search_incidents(
        session=session,
        service_name=service_name,
        severity=severity,
        status=status,
    )

    return {
        "incidents": [
            {
                "service": incident.service.name,
                "title": incident.title,
                "description": incident.description,
                "severity": incident.severity,
                "status": incident.status,
                "detected_at": incident.detected_at.isoformat(),
                "resolved_at": (
                    incident.resolved_at.isoformat()
                    if incident.resolved_at
                    else None
                ),
                "root_cause": incident.root_cause,
            }
            for incident in incidents
        ],
        "count": len(incidents),
    }


@router.get("/stats")
def get_incident_statistics(
    service_name: str | None = None,
    session: Session = Depends(get_db),
) -> dict:
    return get_incident_stats(
        session=session,
        service_name=service_name,
    )