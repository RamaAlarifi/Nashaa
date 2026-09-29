# syntax=docker/dockerfile:1.6
# Nashaa FastAPI backend image (Nashaa_Guide.md §25).
# Multi-stage: a builder stage creates an isolated virtualenv; the runtime
# stage copies only that venv + the application and runs as a non-root user.

# ---- Builder: install dependencies into a virtualenv ----------------------
FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

WORKDIR /tmp/build
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- Runtime: minimal, non-root -----------------------------------------
FROM python:3.10-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/venv/bin:$PATH

# Non-root user (fixed uid/gid).
RUN groupadd --system --gid 10001 nashaa \
 && useradd  --system --uid 10001 --gid nashaa --create-home --home-dir /home/nashaa nashaa

WORKDIR /app

# Copy the prebuilt virtualenv (no pip/setuptools tooling needed at runtime).
COPY --from=builder /opt/venv /opt/venv

# Copy only what the server needs: the app, migrations, alembic config, and
# the startup entrypoint. Tests, .env, .venv, caches, and .git are excluded
# via .dockerignore.
COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh && chmod +x /usr/local/bin/docker-entrypoint.sh

COPY tests ./tests
COPY pytest.ini ./

USER nashaa

EXPOSE 8000

# The entrypoint runs migrations (and optional demo data) before exec'ing the
# CMD. For multi-instance production, run migrations as a separate one-time
# step and override the entrypoint (see README.md).
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
