"""Application settings loaded from environment variables.

All secrets come from the environment or a local ``.env`` file that is never
committed. See ``backend/.env.example`` for the full list of settings.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="postgresql+psycopg://nashaa:nashaa_dev_password@localhost:5432/nashaa"
    )

    # Security
    secret_key: str = Field(default="change-me-to-a-long-random-string")
    session_expire_seconds: int = Field(default=1209600)  # 14 days
    reset_expire_seconds: int = Field(default=1800)  # 30 minutes

    # CORS
    frontend_origin: str = Field(default="http://localhost:3000")

    # AI provider
    ai_provider: Literal["gemini", "mock"] = Field(default="gemini")
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-1.5-flash")
    ai_timeout_seconds: int = Field(default=60)

    # App
    app_name: str = Field(default="Nashaa")
    environment: Literal["development", "testing", "production"] = Field(
        default="development"
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
