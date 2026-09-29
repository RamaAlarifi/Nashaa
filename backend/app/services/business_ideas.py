"""Business idea service (US05, US08): CRUD, revision tracking, visibility."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.business_idea import BusinessIdea
from app.models.enums import IdeaVisibility
from app.models.user import User
from app.schemas.business_idea import (
    BusinessIdeaCreate,
    BusinessIdeaUpdate,
    VisibilityUpdate,
)
from app.services.errors import IdeaNotFound, NotOwner, VisibilityBlocked

# Fields whose change means the assessment is out of date and the idea's
# revision number must increment (US05/US07).
ASSESSMENT_RELATED_FIELDS = (
    "problem",
    "solution",
    "industry",
    "business_stage",
    "target_location",
    "intended_customers",
    "budget",
    "current_challenges",
)


def create_idea(db: Session, owner: User, payload: BusinessIdeaCreate) -> BusinessIdea:
    idea = BusinessIdea(owner_id=owner.id, **payload.model_dump())
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea


def _get_owned_idea(db: Session, idea_id: uuid.UUID, user: User) -> BusinessIdea:
    idea = db.get(BusinessIdea, idea_id)
    if idea is None:
        raise IdeaNotFound("Business idea not found.")
    if idea.owner_id != user.id:
        raise NotOwner("You can only access your own business ideas.")
    return idea


def get_owner_idea(db: Session, idea_id: uuid.UUID, user: User) -> BusinessIdea:
    """Used for owner-only actions (edit, delete, generate assessment)."""
    return _get_owned_idea(db, idea_id, user)


def view_idea(db: Session, idea_id: uuid.UUID, viewer: User) -> tuple[BusinessIdea, bool]:
    """Return (idea, is_full_access).

    Full access when viewer is the owner. Under 'registered' visibility a
    signed-in non-owner gets the summary fields only (is_full_access=False).
    Private ideas are hidden from non-owners (VisibilityBlocked).
    """
    idea = db.get(BusinessIdea, idea_id)
    if idea is None:
        raise IdeaNotFound("Business idea not found.")

    if idea.owner_id == viewer.id:
        return idea, True

    if idea.visibility == IdeaVisibility.REGISTERED:
        return idea, False

    # Private: non-owners must not even learn the idea exists.
    raise VisibilityBlocked("This business idea is private.")


def list_own_ideas(db: Session, user: User) -> list[BusinessIdea]:
    return list(
        db.execute(
            select(BusinessIdea)
            .where(BusinessIdea.owner_id == user.id)
            .order_by(BusinessIdea.updated_at.desc())
        ).scalars().all()
    )


def list_visible_ideas(db: Session, viewer: User) -> list[BusinessIdea]:
    """Ideas visible to a signed-in non-owner user (US08)."""
    return list(
        db.execute(
            select(BusinessIdea)
            .where(
                BusinessIdea.owner_id != viewer.id,
                BusinessIdea.visibility == IdeaVisibility.REGISTERED,
            )
            .order_by(BusinessIdea.updated_at.desc())
        ).scalars().all()
    )


def update_idea(
    db: Session, idea_id: uuid.UUID, user: User, payload: BusinessIdeaUpdate
) -> BusinessIdea:
    idea = _get_owned_idea(db, idea_id, user)
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return idea

    assessment_related_changed = False
    for field, value in changes.items():
        if field in ASSESSMENT_RELATED_FIELDS and getattr(idea, field) != value:
            assessment_related_changed = True
        setattr(idea, field, value)

    if assessment_related_changed:
        idea.revision_number += 1

    db.commit()
    db.refresh(idea)
    return idea


def update_visibility(
    db: Session, idea_id: uuid.UUID, user: User, payload: VisibilityUpdate
) -> BusinessIdea:
    idea = _get_owned_idea(db, idea_id, user)
    idea.visibility = payload.visibility
    db.commit()
    db.refresh(idea)
    return idea


def delete_idea(db: Session, idea_id: uuid.UUID, user: User) -> None:
    idea = _get_owned_idea(db, idea_id, user)
    db.delete(idea)
    db.commit()
