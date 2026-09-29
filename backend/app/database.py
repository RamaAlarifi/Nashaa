"""Database engine, session factory, and helpers.

The declarative ``Base`` lives in :mod:`app.models.base` so it is co-located
with the models. Tables are created from the declarative models via
``create_all`` for development / first run / tests. Migrations (Alembic) can be
added in a later sprint when the schema evolves; for now the schema is stable
and reproducible.
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
