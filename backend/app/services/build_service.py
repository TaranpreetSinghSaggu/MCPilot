from sqlalchemy.orm import Session

from backend.app.models import BuildRun, Repository


def search_builds(
    session: Session,
    repository_name: str | None = None,
    status: str | None = None,
) -> list[BuildRun]:

    query = session.query(BuildRun)

    if repository_name:
        query = query.join(Repository).filter(
            Repository.name == repository_name
        )

    if status:
        query = query.filter(BuildRun.status == status)

    return query.order_by(BuildRun.started_at.desc()).all()

def get_slowest_builds(
    session: Session,
    repository_name: str | None = None,
    limit: int = 5,
) -> list[BuildRun]:

    query = session.query(BuildRun)

    if repository_name:
        query = query.join(Repository).filter(
            Repository.name == repository_name
        )

    return (
        query.order_by(BuildRun.duration_seconds.desc())
        .limit(limit)
        .all()
    )