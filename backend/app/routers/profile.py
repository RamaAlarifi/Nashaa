"""Profile endpoints (US03)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.enums import AccountStatus, ProfileVisibility, Role
from app.models.profile import Profile
from app.models.opportunities import InvestorPreference
from app.industries import CATALOG, validate_industry
from app.models.user import User
from app.schemas.profile import ProfileOut, ProfileUpdate

router = APIRouter(prefix="/api", tags=["profile"])


@router.get("/industries")
def industries():
    return [{"id": code, "label": label} for code, label, _ in CATALOG]


@router.get("/profiles")
def discover_profiles(industry: str = Query("", max_length=120), role: Role | None = None,
    q: str = Query("", max_length=120), limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    category = validate_industry(industry)
    query = select(User).join(Profile, Profile.user_id == User.id).outerjoin(InvestorPreference, InvestorPreference.user_id == User.id).where(
        User.account_status == AccountStatus.ACTIVE, User.role != Role.ADMIN, User.id != user.id,
        Profile.profile_visibility != ProfileVisibility.PRIVATE)
    if role:
        query = query.where(User.role == role)
    if q:
        term = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        query = query.where(or_(Profile.display_name.ilike(term, escape="\\"), Profile.short_description.ilike(term, escape="\\")))
    if category:
        query = query.where(or_((User.role == Role.BUSINESS_OWNER) & (Profile.role_specific_info["industry"].astext == category),
            (User.role == Role.INVESTOR) & InvestorPreference.industries.contains([category])))
    rows = db.scalars(query.order_by(Profile.display_name, User.id).offset(offset).limit(limit)).all()
    result = []
    for other in rows:
        pref = db.scalar(select(InvestorPreference).where(InvestorPreference.user_id == other.id)) if other.role == Role.INVESTOR else None
        selected = pref.industries if pref else [other.profile.role_specific_info.get("industry", "")] if other.role == Role.BUSINESS_OWNER else []
        result.append({"user_id": other.id, "display_name": other.profile.display_name, "role": other.role,
            "location": other.profile.location, "short_description": other.profile.short_description,
            "industries": [i for i in selected if i]})
    return result


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
    allowed = {
        "business_owner": {"business_name", "industry", "industry_detail"},
        "innovator": {"skills", "experience"},
        "investor": {"investment_interests", "preferred_stage"},
        "admin": set(),
    }[user.role.value]
    info = changes.get("role_specific_info")
    if info is not None and any(k not in allowed or not isinstance(v, str) or len(v) > 2000 for k, v in info.items()):
        raise HTTPException(status_code=422, detail="Use the profile fields available for your account role.")
    if info is not None and user.role == Role.BUSINESS_OWNER:
        if "industry" in info:
            info["industry"] = validate_industry(info["industry"], profile.role_specific_info.get("industry"))
        if len(info.get("industry_detail", "")) > 240:
            raise HTTPException(422, "Industry specialisation must be at most 240 characters.")
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
    if other is None or other.profile is None or other.account_status != AccountStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    profile = other.profile
    if profile.profile_visibility == ProfileVisibility.PRIVATE and other.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This profile is private.",
        )
    return profile
