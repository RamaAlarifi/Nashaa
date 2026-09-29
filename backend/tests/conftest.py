"""Pytest configuration and shared fixtures.

Tests run against a separate ``nashaa_test`` database so the seeded development
data is never affected. Each test runs inside a savepoint that is rolled back,
so tests are isolated and fast.

The AI provider can be swapped per test via the ``with_ai_provider`` fixture so
we can exercise success, failure, invalid-response, and slow-provider cases
without hitting a real LLM.
"""

from __future__ import annotations

import os

# Configure test environment before the app reads settings. These take
# priority over .env (pydantic-settings reads real env vars first).
os.environ["ENVIRONMENT"] = "testing"
os.environ["AI_PROVIDER"] = "mock"
os.environ["SMTP_HOST"] = ""
os.environ["EXPOSE_RESET_TOKENS"] = "false"

from collections.abc import Generator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app import models  # noqa: F401, E402  (register models on metadata)
from app.ai.base import AssessmentProvider  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.database import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.base import Base  # noqa: E402

# Force settings to reflect the test environment.
get_settings.cache_clear()
_settings = get_settings()

TEST_DB_NAME = "nashaa_test"
_BASE_URL = _settings.database_url.rsplit("/", 1)[0]  # ...://user:pwd@host:port
TEST_DATABASE_URL = f"{_BASE_URL}/{TEST_DB_NAME}"


@pytest.fixture(scope="session")
def test_engine():
    # Create (or recreate) the test database on a fresh connection.
    admin = create_engine(f"{_BASE_URL}/postgres", isolation_level="AUTOCOMMIT", future=True)
    with admin.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
    admin.dispose()

    eng = create_engine(TEST_DATABASE_URL, pool_pre_ping=True, future=True)
    from alembic.config import Config
    from alembic import command
    config = Config("alembic.ini")
    config.attributes["database_url"] = TEST_DATABASE_URL
    command.upgrade(config, "head")
    yield eng
    eng.dispose()

    admin2 = create_engine(f"{_BASE_URL}/postgres", isolation_level="AUTOCOMMIT", future=True)
    with admin2.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
    admin2.dispose()


@pytest.fixture
def db(test_engine) -> Generator[Session, None, None]:
    """A session isolated by a savepoint; rolled back after the test."""
    conn = test_engine.connect()
    trans = conn.begin()
    session = Session(bind=conn, join_transaction_mode="create_savepoint", expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        conn.close()


@pytest.fixture
def client(db) -> Generator[TestClient, None, None]:
    def _override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def with_ai_provider(monkeypatch):
    """Return a function that installs a custom AI provider for the service."""
    def _install(provider: AssessmentProvider) -> None:
        monkeypatch.setattr("app.services.assessment.get_assessment_provider", lambda: provider)

    return _install


# ---------- Authentication helpers ----------

def _register(client, email="newowner@nashaa.sa", password="Password123!",
              role="business_owner", display_name="New Owner"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "role": role, "display_name": display_name},
    )


def register_and_login(client, **kwargs):
    """Register a user and return (response_json, token)."""
    email = kwargs.pop("email", "newowner@nashaa.sa")
    if kwargs.get("role") == "admin":
        from app.services.auth import create_user, create_session
        from app.models.enums import Role
        from app.database import get_db
        db = next(app.dependency_overrides[get_db]())
        user = create_user(db, email=email, password=kwargs.get("password", "Password123!"), role=Role.ADMIN, display_name=kwargs.get("display_name", "Admin"))
        _, token = create_session(db, user)
        return {"user": {"id": str(user.id)}}, token
    res = _register(client, email=email, **kwargs)
    assert res.status_code == 201, res.text
    data = res.json()
    return data, data["token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
