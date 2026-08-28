from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import DATABASE_URL
from backend.app.mcp.tools.builds import (
    get_slowest_builds_tool,
    search_builds_tool,
)


engine = create_engine(DATABASE_URL)


def test_search_builds_tool():
    with Session(engine) as session:
        result = search_builds_tool(session)

        assert result["count"] == 60
        assert len(result["builds"]) == 60


def test_search_failed_builds_tool():
    with Session(engine) as session:
        result = search_builds_tool(
            session,
            status="failed",
        )

        assert result["count"] > 0

        for build in result["builds"]:
            assert build["status"] == "failed"


def test_search_builds_for_repository():
    with Session(engine) as session:
        result = search_builds_tool(
            session,
            repository_name="mcpilot-api",
        )

        assert result["count"] > 0

        for build in result["builds"]:
            assert build["repository"] == "mcpilot-api"


def test_get_slowest_builds_tool():
    with Session(engine) as session:
        result = get_slowest_builds_tool(
            session,
            limit=5,
        )

        assert result["count"] == 5
        assert len(result["builds"]) == 5

        durations = [
            build["duration_seconds"]
            for build in result["builds"]
        ]

        assert durations == sorted(
            durations,
            reverse=True,
        )


def test_get_slowest_builds_for_repository():
    with Session(engine) as session:
        result = get_slowest_builds_tool(
            session,
            repository_name="mcpilot-api",
            limit=3,
        )

        assert result["count"] == 3
        assert len(result["builds"]) == 3

        for build in result["builds"]:
            assert build["repository"] == "mcpilot-api"