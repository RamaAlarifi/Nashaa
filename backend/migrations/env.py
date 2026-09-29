"""Alembic environment for Nashaa.

The database URL is read from the application settings (``app.config``), so the
same ``.env`` / environment variables drive both the server and the migrations.
Both offline (``alembic`` SQL generation) and online (direct connection) modes
are supported.

Tests keep using ``Base.metadata.create_all`` directly (see tests/conftest.py);
Alembic is the repeatable schema path for development and deployment.
"""

from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure the backend root (where `app` lives) is importable when alembic is run
# from a subdirectory or via the Docker entrypoint.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings  # noqa: E402
from app.models.base import Base  # noqa: E402
from app import models  # noqa: E402,F401  (register models on metadata)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use the app's DATABASE_URL as the single source of truth.
config.set_main_option("sqlalchemy.url", str(config.attributes.get("database_url", get_settings().database_url)).replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
