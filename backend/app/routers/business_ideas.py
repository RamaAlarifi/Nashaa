"""Business idea endpoints (US05, US08)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_business_owner
from app.database import get_db
from app.models.user import User
from app.schemas.business_idea import (
    BusinessIdeaCreate,
    BusinessIdeaOut,
    BusinessIdeaSummary,
    BusinessIdeaUpdate,
    VisibilityUpdate,
)
from app.services import business_ideas as idea_service
from app.services.errors import IdeaNotFound, NotOwner, VisibilityBlocked

router = APIRouter(prefix="/api/ideas", tags=["business-ideas"])


def _to_out(idea) -> BusinessIdeaOut:
    return BusinessIdeaOut.model_validate(idea)


def _to_summary(idea) -> BusinessIdeaSummary:
    return BusinessIdeaSummary.model_validate(idea)


@router.get("", response_model=list[BusinessIdeaOut])
def list_my_ideas(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List the current user's own ideas (full access)."""
    ideas = idea_service.list_own_ideas(db, user)
    return [_to_out(i) for i in ideas]


@router.get("/browse", response_model=list[BusinessIdeaSummary])
def browse_visible_ideas(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Browse ideas other owners have marked visible to registered users."""
    ideas = idea_service.list_visible_ideas(db, user)
    return [_to_summary(i) for i in ideas]


@router.post("", response_model=BusinessIdeaOut, status_code=status.HTTP_201_CREATED)
def create_idea(
    payload: BusinessIdeaCreate,
    owner: User = Depends(require_business_owner),
    db: Session = Depends(get_db),
):
    idea = idea_service.create_idea(db, owner, payload)
    return _to_out(idea)


@router.get("/{idea_id}")
def get_idea(
    idea_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """View a single idea. Returns full detail for the owner, a reduced summary
    for other signed-in users under 'registered' visibility, and 404 for private
    ideas owned by someone else (so private information stays hidden)."""
    try:
        idea, full_access = idea_service.view_idea(db, idea_id, user)
    except IdeaNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except VisibilityBlocked:
        # Hide private ideas from non-owners: respond 404, not 403, so the
        # existence of a private record is not leaked.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business idea not found.")

    if full_access:
        return _to_out(idea)
    return _to_summary(idea)


@router.put("/{idea_id}", response_model=BusinessIdeaOut)
def update_idea(
    idea_id: uuid.UUID,
    payload: BusinessIdeaUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        idea = idea_service.update_idea(db, idea_id, user, payload)
    except IdeaNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except NotOwner as exc:
        # Report 404 to avoid leaking other users' private records.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business idea not found.")
    return _to_out(idea)


@router.patch("/{idea_id}/visibility", response_model=BusinessIdeaOut)
def set_visibility(
    idea_id: uuid.UUID,
    payload: VisibilityUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        idea = idea_service.update_visibility(db, idea_id, user, payload)
    except IdeaNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except NotOwner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business idea not found.")
    return _to_out(idea)


@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_idea(
    idea_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        idea_service.delete_idea(db, idea_id, user)
    except IdeaNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except NotOwner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business idea not found.")
    return None
