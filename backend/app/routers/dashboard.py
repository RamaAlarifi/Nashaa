"""Role-based dashboard endpoint (US04)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.assessment import Assessment
from app.models.business_idea import BusinessIdea
from app.models.enums import AssessmentStatus, Role
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


class IdeaSummaryItem(BaseModel):
    id: str
    name: str
    industry: str
    business_stage: str
    visibility: str
    revision_number: int
    assessment_status: str  # none | in_progress | succeeded | failed


class DashboardOut(BaseModel):
    role: Role
    display_name: str
    # Role-specific content. Fields are populated per role (US04).
    ideas: list[IdeaSummaryItem] | None = None
    message: str | None = None


@router.get("", response_model=DashboardOut)
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    display_name = user.profile.display_name if user.profile else user.email

    if user.role == Role.BUSINESS_OWNER:
        ideas = list(
            db.execute(
                select(BusinessIdea).where(BusinessIdea.owner_id == user.id)
            ).scalars().all()
        )
        items = []
        for idea in ideas:
            latest = db.execute(
                select(Assessment)
                .where(Assessment.idea_id == idea.id)
                .order_by(Assessment.seq.desc())
                .limit(1)
            ).scalar_one_or_none()
            status_val = latest.generation_status.value if latest else "none"
            items.append(
                IdeaSummaryItem(
                    id=str(idea.id),
                    name=idea.name,
                    industry=idea.industry,
                    business_stage=idea.business_stage.value,
                    visibility=idea.visibility.value,
                    revision_number=idea.revision_number,
                    assessment_status=status_val,
                )
            )
        return DashboardOut(
            role=user.role,
            display_name=display_name,
            ideas=items,
        )

    if user.role == Role.INNOVATOR:
        return DashboardOut(
            role=user.role,
            display_name=display_name,
            message="Manage your professional profile, skills, and experience.",
        )

    if user.role == Role.INVESTOR:
        return DashboardOut(
            role=user.role,
            display_name=display_name,
            message="Manage your investor profile and investment interests.",
        )

    if user.role == Role.ADMIN:
        return DashboardOut(
            role=user.role,
            display_name=display_name,
            message="Manage your administrator account and profile.",
        )

    return DashboardOut(role=user.role, display_name=display_name)
