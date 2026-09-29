#!/bin/sh
# Nashaa backend container entrypoint (Nashaa_Guide.md §25).
#   1. Wait for the database and run pending migrations once.
#   2. Optionally load fictional demo data (LOAD_DEMO_DATA=true), off by default.
#   3. exec the container command (uvicorn).
set -e

# Migrations with a bounded retry so the backend can start slightly before the
# database is fully accepting connections (compose health usually handles this;
# the retry adds resilience when run standalone).
i=0
until alembic upgrade head; do
  i=$((i + 1))
  if [ "$i" -ge 10 ]; then
    echo "Database migrations failed after $i attempts." >&2
    exit 1
  fi
  echo "Database not ready yet (attempt $i/10). Retrying in 2s…" >&2
  sleep 2
done

if [ "${LOAD_DEMO_DATA}" = "true" ]; then
  if [ "${ENVIRONMENT}" = "production" ]; then
    echo "Fictional seed data is disabled in production." >&2
    exit 1
  fi
  echo "LOAD_DEMO_DATA=true — loading fictional demo data…"
  python -m app.seed.seed
fi

exec "$@"
