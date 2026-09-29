"""AI provider package.

All AI calls live behind this single component so the provider can be changed
without rewriting the rest of the application (project rule, section 9).
"""

from app.ai.base import (
    AIResponseError,
    AIServiceError,
    AITimeoutError,
    AssessmentInput,
    AssessmentProvider,
    AssessmentResult,
)
from app.ai.factory import get_assessment_provider

__all__ = [
    "AIServiceError",
    "AIResponseError",
    "AITimeoutError",
    "AssessmentInput",
    "AssessmentProvider",
    "AssessmentResult",
    "get_assessment_provider",
]
