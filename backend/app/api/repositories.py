from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.services.repository_service import list_repositories


router = APIRouter(
    prefix="/repositories",
    tags=["repositories"],
)


@router.get("")
def get_repositories(
    language: str | None = None,
    team: str | None = None,
    visibility: str | None = None,
    session: Session = Depends(get_db),
) -> dict:
    repositories = list_repositories(
        session=session,
        language=language,
        team=team,
        visibility=visibility,
    )

    return {
        "repositories": [
            {
                "name": repository.name,
                "description": repository.description,
                "language": repository.language,
                "team": repository.team,
                "visibility": repository.visibility,
            }
            for repository in repositories
        ],
        "count": len(repositories),
    }