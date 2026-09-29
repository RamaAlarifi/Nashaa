"""Profile endpoints (US03)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.enums import ProfileVisibility
from app.models.user import User
from app.schemas.profile import ProfileOut, ProfileUpdate

router = APIRouter(prefix="/api", tags=["profile"])


@router.get("/profile", response_model=ProfileOut)
def get_my_profile(user: User = Depends(get_current_user)):
    if user.profile is None:  # pragma: no cover - create_user always makes one
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    return user.profile


@router.put("/profile", response_model=ProfileOut)
def update_my_profile(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.profile is None:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    profile = user.profile
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/users/{user_id}/profile", response_model=ProfileOut)
def view_profile(
    user_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """View another user's profile, respecting profile visibility.

    - PUBLIC: visible to anyone signed in.
    - REGISTERED: visible to signed-in users (always satisfied here).
    - PRIVATE: visible only to the owner.
    Role is never exposed as editable and is not part of ProfileOut.
    """
    other = db.get(User, user_id)
    if other is None or other.profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    profile = other.profile
    if profile.profile_visibility == ProfileVisibility.PRIVATE and other.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This profile is private.",
        )
    return profile
