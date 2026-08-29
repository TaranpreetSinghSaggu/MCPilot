from sqlalchemy.orm import Session

from backend.app.mcp.schemas import Repository, RepositorySearchResult
from backend.app.services.repository_service import list_repositories


def search_repositories(
    session: Session,
    language: str | None = None,
    team: str | None = None,
    visibility: str | None = None,
) -> RepositorySearchResult:

    repositories = list_repositories(
        session=session,
        language=language,
        team=team,
        visibility=visibility,
    )

    return RepositorySearchResult(
        repositories=[
            Repository(
                name=repository.name,
                description=repository.description,
                language=repository.language,
                team=repository.team,
                visibility=repository.visibility,
            )
            for repository in repositories
        ],
        count=len(repositories),
    )