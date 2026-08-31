from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.services.build_service import (
    get_slowest_builds,
    search_builds,
)


router = APIRouter(
    prefix="/builds",
    tags=["builds"],
)


@router.get("")
def get_builds(
    repository_name: str | None = None,
    status: str | None = None,
    session: Session = Depends(get_db),
) -> dict:
    builds = search_builds(
        session=session,
        repository_name=repository_name,
        status=status,
    )

    return {
        "builds": [
            {
                "repository": build.repository.name,
                "commit_id": build.commit_id,
                "status": build.status,
                "duration_seconds": build.duration_seconds,
                "started_at": build.started_at.isoformat(),
                "finished_at": build.finished_at.isoformat(),
            }
            for build in builds
        ],
        "count": len(builds),
    }


@router.get("/slowest")
def get_slowest_build_runs(
    repository_name: str | None = None,
    limit: int = 5,
    session: Session = Depends(get_db),
) -> dict:
    builds = get_slowest_builds(
        session=session,
        repository_name=repository_name,
        limit=limit,
    )

    return {
        "builds": [
            {
                "repository": build.repository.name,
                "commit_id": build.commit_id,
                "status": build.status,
                "duration_seconds": build.duration_seconds,
                "started_at": build.started_at.isoformat(),
                "finished_at": build.finished_at.isoformat(),
            }
            for build in builds
        ],
        "count": len(builds),
    }