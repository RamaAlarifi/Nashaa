"""Abstract assessment provider and shared data structures."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from app.models.enums import BusinessStage


class AIServiceError(Exception):
    """Base error for any AI provider failure (network, HTTP, parsing)."""


class AITimeoutError(AIServiceError):
    """The AI provider did not respond in time."""


class AIResponseError(AIServiceError):
    """The AI provider returned a response we could not parse or validate."""


class AssessmentInput(BaseModel):
    """The idea data passed to a provider to generate an assessment."""

    name: str
    problem: str
    solution: str
    industry: str
    business_stage: BusinessStage
    target_location: str
    intended_customers: str
    budget: str
    current_challenges: str


class AssessmentResult(BaseModel):
    """A validated, structured assessment (US06 required fields)."""

    market_considerations: str = ""
    target_customer_analysis: str = ""
    competitor_considerations: str = ""
    indicative_costs: str = ""
    suggested_next_steps: str = ""
    assumptions: str = ""
    sources: str = ""

    @classmethod
    def from_mapping(cls, data: dict) -> "AssessmentResult":
        """Validate a parsed mapping, coercing/trimming strings.

        Raises AIResponseError if the mapping is missing required keys or the
        values are not strings.
        """
        required = {
            "market_considerations",
            "target_customer_analysis",
            "competitor_considerations",
            "indicative_costs",
            "suggested_next_steps",
            "assumptions",
        }
        missing = [k for k in required if k not in data]
        if missing:
            raise AIResponseError(f"AI response missing required fields: {missing}")

        def _text(key: str) -> str:
            value = data.get(key, "")
            if value is None:
                return ""
            if isinstance(value, (list, tuple)):
                # Join list-valued fields into a single string.
                return "\n".join(str(item) for item in value).strip()
            if isinstance(value, dict):
                import json

                return json.dumps(value, ensure_ascii=False, indent=2)
            return str(value).strip()

        return cls(
            market_considerations=_text("market_considerations"),
            target_customer_analysis=_text("target_customer_analysis"),
            competitor_considerations=_text("competitor_considerations"),
            indicative_costs=_text("indicative_costs"),
            suggested_next_steps=_text("suggested_next_steps"),
            assumptions=_text("assumptions"),
            sources=_text("sources") if "sources" in data else "",
        )


class AssessmentProvider(ABC):
    """Implementations must return a fully validated AssessmentResult."""

    @abstractmethod
    def generate(self, data: AssessmentInput) -> AssessmentResult:
        """Generate an assessment. Raise AIServiceError on any failure."""
        raise NotImplementedError
