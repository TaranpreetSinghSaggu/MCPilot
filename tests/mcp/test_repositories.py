from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import DATABASE_URL
from backend.app.mcp.tools.repositories import search_repositories


engine = create_engine(DATABASE_URL)


def test_search_repositories():
    with Session(engine) as session:
        result = search_repositories(session)

        assert result["count"] == 5
        assert len(result["repositories"]) == 5


def test_search_repositories_by_language():
    with Session(engine) as session:
        result = search_repositories(
            session,
            language="Python",
        )

        assert result["count"] > 0

        for repository in result["repositories"]:
            assert repository["language"] == "Python"


def test_search_repositories_by_visibility():
    with Session(engine) as session:
        result = search_repositories(
            session,
            visibility="private",
        )

        assert result["count"] > 0

        for repository in result["repositories"]:
            assert repository["visibility"] == "private"


def test_search_repositories_with_multiple_filters():
    with Session(engine) as session:
        result = search_repositories(
            session,
            language="Python",
            visibility="private",
        )

        for repository in result["repositories"]:
            assert repository["language"] == "Python"
            assert repository["visibility"] == "private"