"""Application settings loaded from environment variables.

All secrets come from the environment or a local ``.env`` file that is never
committed. See ``backend/.env.example`` for the full list of settings.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
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
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_starttls: bool = True
    reset_url: str = "http://localhost:3000/reset-password"
    expose_reset_tokens: bool = False

    # CORS
    frontend_origin: str = Field(default="http://localhost:3000")

    # AI provider
    ai_provider: Literal["gemini", "mock"] = Field(default="mock")
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="")
    ai_timeout_seconds: int = Field(default=60)

    # App
    app_name: str = Field(default="Nashaa")
    environment: Literal["development", "testing", "production"] = Field(
        default="development"
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()]

    @model_validator(mode="after")
    def production_settings(self):
        if self.environment == "production":
            if not self.smtp_host or not self.smtp_from or not self.smtp_starttls:
                raise ValueError("Production requires SMTP_HOST, SMTP_FROM and SMTP_STARTTLS=true.")
            if not self.reset_url.startswith("https://") or any(not origin.startswith("https://") for origin in self.cors_origins):
                raise ValueError("Production requires HTTPS frontend and reset URLs.")
            if self.expose_reset_tokens:
                raise ValueError("Reset-token exposure is disabled in production.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
