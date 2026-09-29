"""Assessment endpoints (US06, US07)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.assessment import AssessmentStatusOut
from app.services import assessment as assessment_service
from app.services.errors import (
    AssessmentInProgress,
    IdeaNotFound,
    NotOwner,
)

router = APIRouter(prefix="/api/ideas", tags=["assessments"])


@router.get("/{idea_id}/assessment", response_model=AssessmentStatusOut)
def get_assessment_status(
    idea_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return assessment_service.get_assessment_status(db, idea_id, user)
    except IdeaNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except NotOwner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business idea not found.")


@router.post("/{idea_id}/assessment", response_model=AssessmentStatusOut)
def generate_assessment(
    idea_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        assessment_service.generate_assessment(db, idea_id, user)
    except IdeaNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except NotOwner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business idea not found.")
    except AssessmentInProgress as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return assessment_service.get_assessment_status(db, idea_id, user)
