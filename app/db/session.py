from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def create_db_engine():
    settings = get_settings()
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(
        settings.database_url,
        connect_args=connect_args,
        echo=settings.app_debug,
    )


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    from app.db import models  # noqa: F401 (ensure models are loaded)

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
