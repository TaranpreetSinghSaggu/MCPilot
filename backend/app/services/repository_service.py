from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models import (
    Commit,
    Issue,
    PullRequest,
    Repository,
    BuildRun,
)


def list_repositories(
    session: Session,
    language: str | None = None,
    team: str | None = None,
    visibility: str | None = None,
) -> list[Repository]:

    query = session.query(Repository)

    if language:
        query = query.filter(Repository.language == language)

    if team:
        query = query.filter(Repository.team == team)

    if visibility:
        query = query.filter(Repository.visibility == visibility)

    return query.order_by(Repository.name).all()


def get_repository_stats(
    session: Session,
    repository_name: str,
) -> dict:

    repository = (
        session.query(Repository)
        .filter(Repository.name == repository_name)
        .first()
    )

    if repository is None:
        raise ValueError(f"Repository not found: {repository_name}")

    commit_count = (
        session.query(func.count(Commit.id))
        .filter(Commit.repository_id == repository.id)
        .scalar()
    )

    pull_request_count = (
        session.query(func.count(PullRequest.id))
        .filter(PullRequest.repository_id == repository.id)
        .scalar()
    )

    issue_count = (
        session.query(func.count(Issue.id))
        .filter(Issue.repository_id == repository.id)
        .scalar()
    )

    build_count = (
        session.query(func.count(BuildRun.id))
        .filter(BuildRun.repository_id == repository.id)
        .scalar()
    )

    return {
        "repository": repository.name,
        "commit_count": commit_count,
        "pull_request_count": pull_request_count,
        "issue_count": issue_count,
        "build_count": build_count,
    }