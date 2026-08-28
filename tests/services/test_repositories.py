from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import DATABASE_URL
from backend.app.services.repository_service import (
    get_repository_stats,
    list_repositories,
)


engine = create_engine(DATABASE_URL)


def test_list_repositories():
    with Session(engine) as session:
        repositories = list_repositories(session)

        assert len(repositories) == 5


def test_repository_filters():
    with Session(engine) as session:
        repositories = list_repositories(
            session,
            language="Python",
        )

        assert repositories

        for repository in repositories:
            assert repository.language == "Python"


def test_repository_stats():
    with Session(engine) as session:
        stats = get_repository_stats(
            session,
            "mcpilot-api",
        )

        assert stats["repository"] == "mcpilot-api"
        assert stats["commit_count"] >= 0
        assert stats["pull_request_count"] >= 0
        assert stats["issue_count"] >= 0
        assert stats["build_count"] >= 0