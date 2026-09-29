"""Database engine, session factory, and helpers.

Runtime schema changes use Alembic migrations. init_db is only a model utility
for isolated experiments; Docker and seeds never call it.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models.base import Base

__all__ = ["Base", "engine", "SessionLocal", "get_db", "init_db"]

_settings = get_settings()

engine = create_engine(
    _settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Intended for development / tests / first run."""
    # Import models so they are registered on the Base metadata.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
