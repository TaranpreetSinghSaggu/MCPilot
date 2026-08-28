from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import DATABASE_URL
from backend.app.services.issue_service import search_issues


engine = create_engine(DATABASE_URL)


def test_search_issues():
    with Session(engine) as session:
        issues = search_issues(session)

        assert len(issues) == 30


def test_search_critical_issues():
    with Session(engine) as session:
        issues = search_issues(
            session,
            priority="critical",
        )

        assert issues

        for issue in issues:
            assert issue.priority == "critical"


def test_search_open_issues_for_repository():
    with Session(engine) as session:
        issues = search_issues(
            session,
            repository_name="mcpilot-api",
            status="open",
        )

        for issue in issues:
            assert issue.priority is not None
            assert issue.status == "open"


def test_search_issues_by_assignee():
    with Session(engine) as session:
        issues = search_issues(
            session,
            assignee_username="alice",
        )

        for issue in issues:
            assert issue.assignee is not None
            assert issue.assignee.username == "alice"