"""Business idea schemas (US05, US08)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import BusinessStage, IdeaVisibility
from app.schemas import ORM_CONFIG


class BusinessIdeaBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=200)
    problem: str = ""
    solution: str = ""
    industry: str = Field(default="", max_length=120)
    business_stage: BusinessStage = BusinessStage.IDEA
    target_location: str = Field(default="", max_length=120)
    intended_customers: str = ""
    budget: str = Field(default="", max_length=120)
    current_challenges: str = ""
    visibility: IdeaVisibility = IdeaVisibility.PRIVATE


class BusinessIdeaCreate(BusinessIdeaBase):
    pass


class BusinessIdeaUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def reject_nulls(cls, values):
        if isinstance(values, dict) and any(v is None for v in values.values()):
            raise ValueError("Fields cannot be null. Use an empty string to clear optional text.")
        return values

    name: str | None = Field(default=None, min_length=1, max_length=200)
    problem: str | None = None
    solution: str | None = None
    industry: str | None = Field(default=None, max_length=120)
    business_stage: BusinessStage | None = None
    target_location: str | None = Field(default=None, max_length=120)
    intended_customers: str | None = None
    budget: str | None = Field(default=None, max_length=120)
    current_challenges: str | None = None
    visibility: IdeaVisibility | None = None


class VisibilityUpdate(BaseModel):
    visibility: IdeaVisibility


class BusinessIdeaOut(BaseModel):
    model_config = ORM_CONFIG

    id: UUID
    owner_id: UUID
    name: str
    problem: str
    solution: str
    industry: str
    business_stage: BusinessStage
    target_location: str
    intended_customers: str
    budget: str
    current_challenges: str
    visibility: IdeaVisibility
    revision_number: int
    created_at: datetime
    updated_at: datetime


class BusinessIdeaSummary(BaseModel):
    """Reduced view shown to non-owners under 'registered' visibility.

    Omits sensitive detail fields (problem/solution/challenges/budget) while
    still letting other users see that an idea exists.
    """

    model_config = ORM_CONFIG

    id: UUID
    owner_id: UUID
    name: str
    industry: str
    business_stage: BusinessStage
    target_location: str
    intended_customers: str
    visibility: IdeaVisibility
    revision_number: int
