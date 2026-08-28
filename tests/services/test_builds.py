from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import DATABASE_URL
from backend.app.services.build_service import (
    get_slowest_builds,
    search_builds,
)


engine = create_engine(DATABASE_URL)


def test_search_builds():
    with Session(engine) as session:
        builds = search_builds(session)

        assert len(builds) == 60


def test_search_failed_builds():
    with Session(engine) as session:
        builds = search_builds(
            session,
            status="failed",
        )

        assert builds

        for build in builds:
            assert build.status == "failed"


def test_search_builds_for_repository():
    with Session(engine) as session:
        builds = search_builds(
            session,
            repository_name="mcpilot-api",
        )

        assert builds

        for build in builds:
            assert build.repository.name == "mcpilot-api"


def test_get_slowest_builds():
    with Session(engine) as session:
        builds = get_slowest_builds(
            session,
            limit=5,
        )

        assert len(builds) <= 5

        durations = [
            build.duration_seconds
            for build in builds
        ]

        assert durations == sorted(
            durations,
            reverse=True,
        )


def test_get_slowest_builds_for_repository():
    with Session(engine) as session:
        builds = get_slowest_builds(
            session,
            repository_name="mcpilot-api",
            limit=3,
        )

        assert len(builds) <= 3

        for build in builds:
            assert build.repository.name == "mcpilot-api"