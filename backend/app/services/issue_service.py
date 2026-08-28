from sqlalchemy.orm import Session

from backend.app.models import Issue, Repository, User


def search_issues(
    session: Session,
    repository_name: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    assignee_username: str | None = None,
) -> list[Issue]:

    query = session.query(Issue)

    if repository_name:
        query = query.join(Repository).filter(
            Repository.name == repository_name
        )

    if priority:
        query = query.filter(Issue.priority == priority)

    if status:
        query = query.filter(Issue.status == status)

    if assignee_username:
        query = query.join(
            User,
            Issue.assignee_id == User.id,
        ).filter(
            User.username == assignee_username
        )

    return query.order_by(Issue.created_at.desc()).all()