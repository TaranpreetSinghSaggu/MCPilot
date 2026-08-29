from sqlalchemy.orm import Session

from backend.app.mcp.schemas import Issue, IssueSearchResult
from backend.app.services.issue_service import search_issues


def search_issues_tool(
    session: Session,
    repository_name: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    assignee_username: str | None = None,
) -> IssueSearchResult:

    issues = search_issues(
        session=session,
        repository_name=repository_name,
        priority=priority,
        status=status,
        assignee_username=assignee_username,
    )

    return IssueSearchResult(
        issues=[
            Issue(
                title=issue.title,
                repository=issue.repository.name,
                priority=issue.priority,
                status=issue.status,
                reported_by=issue.reporter.username,
                assignee=(
                    issue.assignee.username
                    if issue.assignee
                    else None
                ),
                created_at=issue.created_at.isoformat(),
                resolved_at=(
                    issue.resolved_at.isoformat()
                    if issue.resolved_at
                    else None
                ),
            )
            for issue in issues
        ],
        count=len(issues),
    )