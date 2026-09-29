"""Nashaa FastAPI application entrypoint.

Run in development with:
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import engine
from sqlalchemy import text
from app.routers import assessments, auth, business_ideas, dashboard, profile

logger = logging.getLogger("nashaa")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Nashaa API",
        description="Nashaa AI Platform for Saudi SMEs — Sprint 1",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(profile.router)
    app.include_router(dashboard.router)
    app.include_router(business_ideas.router)
    app.include_router(assessments.router)

    @app.get("/api/health", tags=["health"])
    def health() -> dict:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "app": settings.app_name, "environment": settings.environment}

    # Generic health probe (Nashaa_Guide.md §25: "such as /health") for container
    # health checks that should not depend on the /api prefix.
    @app.get("/health", tags=["health"])
    def health_root() -> dict:
        return health()

    # Translate 422 validation errors into clear, useful field messages
    # (project rule 6).
    @app.exception_handler(RequestValidationError)
    async def _validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        problems = []
        for err in exc.errors():
            loc = ".".join(str(p) for p in err.get("loc", []) if p not in ("body",))
            problems.append({"field": loc or "body", "message": err.get("msg", "Invalid value.")})
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Please check the highlighted fields and try again.",
                "errors": problems,
            },
        )

    # Catch-all: never leak technical error text to the client.
    @app.exception_handler(Exception)
    async def _unhandled_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server error")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Something went wrong on our side. Please try again shortly."
            },
        )

    return app


app = create_app()
