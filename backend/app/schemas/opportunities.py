"""Validated Sprint 2 commands. Unknown fields never change server-owned state."""
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.enums import BusinessStage

Text120 = Annotated[str, Field(min_length=1, max_length=120)]
Money = Annotated[Decimal, Field(ge=0, le=999999999999, max_digits=14, decimal_places=2)]


class Command(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class ChallengeIn(Command):
    idea_id: UUID | None = None
    title: str = Field(min_length=1, max_length=200)
    problem: str = Field(default="", max_length=10000)
    desired_outcome: str = Field(default="", max_length=10000)
    required_skills: list[Text120] = Field(default_factory=list, max_length=20)
    industry: str = Field(default="", max_length=120)
    location: str = Field(default="", max_length=120)
    timeline: str = Field(default="", max_length=200)
    compensation: str = Field(default="", max_length=200)


class PublishIn(Command):
    approved: Literal[True]


class VerificationIn(Command):
    information: str = Field(min_length=20, max_length=4000)
    reference: str = Field(default="", max_length=500)


class DecisionIn(Command):
    decision: Literal["approved", "rejected"]
    reason: str = Field(min_length=5, max_length=2000)


class ProposalIn(Command):
    approach: str = Field(min_length=10, max_length=10000)
    deliverables: str = Field(min_length=10, max_length=10000)
    timeline: str = Field(min_length=1, max_length=200)
    cost: Money | None = None


class ContactPreferenceIn(Command):
    preference: Literal["open", "contact_request", "closed"]


class ContactIn(Command):
    recipient_id: UUID
    idea_id: UUID | None = None
    challenge_id: UUID | None = None

    @model_validator(mode="after")
    def one_context(self):
        if (self.idea_id is None) == (self.challenge_id is None):
            raise ValueError("Choose exactly one idea or challenge context.")
        return self


class ContactDecisionIn(Command):
    decision: Literal["accepted", "rejected", "revoked"]


class MessageIn(Command):
    body: str = Field(min_length=1, max_length=4000)


class PreferenceIn(Command):
    industries: list[Text120] = Field(min_length=1, max_length=20)
    stages: list[BusinessStage] = Field(min_length=1, max_length=5)
    locations: list[Text120] = Field(default_factory=list, max_length=30)
    min_funding: Money
    max_funding: Money

    @model_validator(mode="after")
    def valid_range(self):
        if self.max_funding < self.min_funding:
            raise ValueError("Maximum funding must be at least the minimum.")
        return self


class HistoryIn(Command):
    project_name: str = Field(min_length=1, max_length=200)
    industry: Text120
    stage: BusinessStage
    source: str = Field(min_length=3, max_length=500)


class FundingIn(Command):
    amount: Money
    currency: Literal["SAR"] = "SAR"


class ShareIn(Command):
    assessment_id: UUID
    investor_id: UUID
    approved: Literal[True]


class SharedAssessmentOut(BaseModel):
    """Deliberately excludes raw inputs, failed attempts and internal errors."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    idea_id: UUID
    idea_revision: int
    provider: str = "unknown"
    created_at: datetime
    market_considerations: str
    target_customer_analysis: str
    competitor_considerations: str
    indicative_costs: str
    suggested_next_steps: str
    assumptions: str
    sources: str
