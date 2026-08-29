from sqlalchemy.orm import Session

from backend.app.mcp.schemas import Build, BuildSearchResult
from backend.app.services.build_service import (
    get_slowest_builds,
    search_builds,
)


def search_builds_tool(
    session: Session,
    repository_name: str | None = None,
    status: str | None = None,
) -> BuildSearchResult:

    builds = search_builds(
        session=session,
        repository_name=repository_name,
        status=status,
    )

    return BuildSearchResult(
        builds=[
            Build(
                repository=build.repository.name,
                commit_id=build.commit_id,
                status=build.status,
                duration_seconds=build.duration_seconds,
                started_at=build.started_at.isoformat(),
                finished_at=build.finished_at.isoformat(),
            )
            for build in builds
        ],
        count=len(builds),
    )


def get_slowest_builds_tool(
    session: Session,
    repository_name: str | None = None,
    limit: int = 5,
) -> BuildSearchResult:

    builds = get_slowest_builds(
        session=session,
        repository_name=repository_name,
        limit=limit,
    )

    return BuildSearchResult(
        builds=[
            Build(
                repository=build.repository.name,
                commit_id=build.commit_id,
                status=build.status,
                duration_seconds=build.duration_seconds,
                started_at=build.started_at.isoformat(),
                finished_at=build.finished_at.isoformat(),
            )
            for build in builds
        ],
        count=len(builds),
    )