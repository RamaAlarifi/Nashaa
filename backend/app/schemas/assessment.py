"""Assessment schemas (US06, US07)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import AssessmentStatus
from app.schemas import ORM_CONFIG


class AssessmentOut(BaseModel):
    model_config = ORM_CONFIG

    id: UUID
    idea_id: UUID
    idea_revision: int
    input_snapshot: dict[str, Any]
    generation_status: AssessmentStatus
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    market_considerations: str
    target_customer_analysis: str
    competitor_considerations: str
    indicative_costs: str
    suggested_next_steps: str
    assumptions: str
    sources: str


class AssessmentStatusOut(BaseModel):
    # "none" when the idea has no assessment attempts yet.
    current_status: str
    latest_attempt_status: AssessmentStatus | None
    latest_valid: AssessmentOut | None
    in_progress: bool
    error_message: str | None
