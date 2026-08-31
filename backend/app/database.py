from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import DATABASE_URL


engine = create_engine(DATABASE_URL)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session