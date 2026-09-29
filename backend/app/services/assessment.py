"""Assessment service (US06, US07).

Key behaviors required by the guide:
- The screen must show generation is in progress (an IN_PROGRESS row is
  persisted before the AI call).
- Two assessment requests cannot run for the same idea at the same time
  (row-lock + IN_PROGRESS check).
- If an AI request fails, the previous successful result remains available
  (each attempt is its own row; we never overwrite a SUCCEEDED assessment).
- The idea revision that produced an assessment is recorded (idea_revision).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import AIServiceError, AssessmentInput, get_assessment_provider
from app.config import get_settings
from app.models.assessment import Assessment
from app.models.business_idea import BusinessIdea
from app.models.enums import AssessmentStatus
from app.models.user import User
from app.schemas.assessment import AssessmentOut, AssessmentStatusOut
from app.services.errors import AssessmentInProgress, IdeaNotFound, NotOwner


def _idea_to_input(idea: BusinessIdea) -> AssessmentInput:
    return AssessmentInput(
        name=idea.name,
        problem=idea.problem,
        solution=idea.solution,
        industry=idea.industry,
        business_stage=idea.business_stage,
        target_location=idea.target_location,
        intended_customers=idea.intended_customers,
        budget=idea.budget,
        current_challenges=idea.current_challenges,
    )


def _input_snapshot(idea: BusinessIdea) -> dict:
    return {
        "name": idea.name,
        "problem": idea.problem,
        "solution": idea.solution,
        "industry": idea.industry,
        "business_stage": idea.business_stage.value,
        "target_location": idea.target_location,
        "intended_customers": idea.intended_customers,
        "budget": idea.budget,
        "current_challenges": idea.current_challenges,
        "revision_number": idea.revision_number,
    }


def _as_utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def get_assessment_status(db: Session, idea_id: uuid.UUID, user: User) -> AssessmentStatusOut:
    """Owner-only view of the current assessment state for an idea."""
    idea = db.get(BusinessIdea, idea_id)
    if idea is None:
        raise IdeaNotFound("Business idea not found.")
    if idea.owner_id != user.id:
        raise NotOwner("You can only view assessments for your own ideas.")

    attempts = list(
        db.execute(
            select(Assessment)
            .where(Assessment.idea_id == idea.id)
            .order_by(Assessment.seq.desc())
        ).scalars().all()
    )

    if not attempts:
        return AssessmentStatusOut(
            current_status="none",
            latest_attempt_status=None,
            latest_valid=None,
            in_progress=False,
            error_message=None,
        )

    latest = attempts[0]
    latest_valid = next(
        (a for a in attempts if a.generation_status == AssessmentStatus.SUCCEEDED), None
    )
    failed = latest.generation_status == AssessmentStatus.FAILED
    return AssessmentStatusOut(
        current_status=latest.generation_status.value,
        latest_attempt_status=latest.generation_status,
        latest_valid=AssessmentOut.model_validate(latest_valid) if latest_valid else None,
        in_progress=latest.generation_status == AssessmentStatus.IN_PROGRESS,
        error_message=latest.error_message if failed else None,
    )


def generate_assessment(db: Session, idea_id: uuid.UUID, user: User) -> Assessment:
    """Generate (or regenerate) an assessment for an idea.

    Returns the created Assessment row (SUCCEEDED or FAILED). Raises
    AssessmentInProgress if a non-stale generation is already running.
    """
    settings = get_settings()

    # Lock the idea row to serialize concurrent assessment requests for it.
    idea = db.execute(
        select(BusinessIdea).where(BusinessIdea.id == idea_id).with_for_update()
    ).scalar_one_or_none()
    if idea is None:
        raise IdeaNotFound("Business idea not found.")
    if idea.owner_id != user.id:
        raise NotOwner("You can only assess your own business ideas.")

    stale_after = timedelta(seconds=max(60, settings.ai_timeout_seconds * 2))
    now = datetime.now(timezone.utc)
    in_progress_rows = list(
        db.execute(
            select(Assessment).where(
                Assessment.idea_id == idea.id,
                Assessment.generation_status == AssessmentStatus.IN_PROGRESS,
            )
        ).scalars().all()
    )
    for row in in_progress_rows:
        if now - _as_utc(row.created_at) < stale_after:
            raise AssessmentInProgress(
                "An assessment is already being generated for this idea. "
                "Please wait for it to finish."
            )
        # Stale (interrupted/timed out) — clean it up so generation can proceed.
        row.generation_status = AssessmentStatus.FAILED
        row.error_message = "Generation was interrupted or timed out."

    # Capture inputs now, before the lock is released by the commit below.
    ai_input = _idea_to_input(idea)
    snapshot = _input_snapshot(idea)
    assessment = Assessment(
        idea_id=idea.id,
        idea_revision=idea.revision_number,
        input_snapshot=snapshot,
        generation_status=AssessmentStatus.IN_PROGRESS,
    )
    db.add(assessment)
    db.commit()  # releases the row lock; persists the IN_PROGRESS row
    db.refresh(assessment)

    # Call the AI provider outside the lock so the idea is not blocked during
    # the (possibly slow) generation.
    try:
        provider = get_assessment_provider()
        result = provider.generate(ai_input)
        from app.ai.base import AssessmentResult
        result = AssessmentResult.from_mapping(result.model_dump())
    except Exception as exc:
        assessment.generation_status = AssessmentStatus.FAILED
        assessment.error_message = "Assessment generation failed. Please try again. Your last successful assessment is preserved."
        db.commit()
        db.refresh(assessment)
        return assessment

    assessment.market_considerations = result.market_considerations
    assessment.target_customer_analysis = result.target_customer_analysis
    assessment.competitor_considerations = result.competitor_considerations
    assessment.indicative_costs = result.indicative_costs
    assessment.suggested_next_steps = result.suggested_next_steps
    assessment.assumptions = result.assumptions
    assessment.sources = result.sources
    assessment.generation_status = AssessmentStatus.SUCCEEDED
    assessment.error_message = None
    db.commit()
    db.refresh(assessment)
    return assessment
