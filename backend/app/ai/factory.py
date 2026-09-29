"""Choose the assessment provider from settings."""

from __future__ import annotations

from app.ai.base import AssessmentProvider, AIServiceError
from app.ai.gemini import GeminiAssessmentProvider
from app.ai.mock import MockAssessmentProvider
from app.config import get_settings

_cached: AssessmentProvider | None = None


def get_assessment_provider() -> AssessmentProvider:
    global _cached
    if _cached is not None:
        return _cached

    settings = get_settings()
    if settings.ai_provider == "mock":
        _cached = MockAssessmentProvider()
        return _cached
    if settings.ai_provider == "gemini":
        # If no key is configured, fall back to mock so the app still runs.
        if not settings.gemini_api_key:
            _cached = MockAssessmentProvider()
            return _cached
        _cached = GeminiAssessmentProvider()
        return _cached
    raise AIServiceError(f"Unknown AI provider: {settings.ai_provider}")


def reset_provider_cache() -> None:
    """Test helper to force re-reading settings after they change."""
    global _cached
    _cached = None
