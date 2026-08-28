from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import DATABASE_URL
from backend.app.mcp.tools.issues import search_issues_tool


engine = create_engine(DATABASE_URL)


def test_search_issues_tool():
    with Session(engine) as session:
        result = search_issues_tool(session)

        assert result["count"] == 30
        assert len(result["issues"]) == 30


def test_search_critical_issues_tool():
    with Session(engine) as session:
        result = search_issues_tool(
            session,
            priority="critical",
        )

        assert result["count"] > 0

        for issue in result["issues"]:
            assert issue["priority"] == "critical"


def test_search_open_issues_for_repository():
    with Session(engine) as session:
        result = search_issues_tool(
            session,
            repository_name="checkout-platform",
            status="open",
        )

        assert result["count"] > 0

        for issue in result["issues"]:
            assert issue["repository"] == "checkout-platform"
            assert issue["status"] == "open"


def test_search_issues_by_assignee():
    with Session(engine) as session:
        result = search_issues_tool(
            session,
            assignee_username="alice",
        )

        assert result["count"] > 0

        for issue in result["issues"]:
            assert issue["assignee"] == "alice"