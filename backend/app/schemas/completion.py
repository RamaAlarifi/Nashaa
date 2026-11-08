from typing import Literal
from uuid import UUID
from pydantic import Field, model_validator
from app.schemas.opportunities import Command

class BodyIn(Command):
    body: str = Field(min_length=1, max_length=4000)

class RatingIn(Command):
    score: int = Field(ge=1, le=5, strict=True)
    comment: str = Field(default="", max_length=2000)

class ProfileDetails(Command):
    customer_type: str = Field(min_length=1, max_length=500)
    industry: str = Field(default="", max_length=120)
    location: str = Field(default="", max_length=120)
    size: str = Field(default="", max_length=500)
    main_need: str = Field(min_length=1, max_length=2000)
    buying_motivation: str = Field(default="", max_length=2000)
    objections: str = Field(default="", max_length=2000)
    channels: str = Field(default="", max_length=2000)
    assumptions: str = Field(default="", max_length=2000)

class GenerateProfileIn(Command):
    kind: Literal["business", "consumer"]

class ProfileIn(GenerateProfileIn):
    details: ProfileDetails

class ImportIn(Command):
    filename: str = Field(pattern=r"^[^/\\]+\.csv$", max_length=200)
    source: str = Field(min_length=5, max_length=500)
    permission_confirmed: Literal[True]
    fictional: bool = False
    csv_text: str = Field(min_length=1, max_length=100000)

class LeadIn(Command):
    kind: Literal["customer", "investor"]
    reference_id: UUID

class LeadStatusIn(Command):
    status: Literal["new", "reviewing", "contact_requested", "contacted", "interested", "not_interested", "follow_up_needed", "closed"]

class ReportIn(Command):
    target_type: Literal["user", "idea", "challenge", "proposal", "collaboration", "message"]
    target_id: UUID
    category: Literal["spam", "abuse", "inappropriate_content", "privacy", "technical", "other"]
    description: str = Field(min_length=10, max_length=4000)

class AdminActionIn(Command):
    target_type: Literal["user", "idea", "challenge", "message"]
    target_id: UUID
    action: Literal["suspend", "reactivate", "deactivate", "hide", "restore", "remove"]
    reason: str = Field(min_length=5, max_length=2000)

class ReportDecisionIn(Command):
    status: Literal["resolved", "dismissed"]
    reason: str = Field(min_length=5, max_length=2000)
    action: AdminActionIn | None = None

class EvaluationIn(Command):
    participant_code: str = Field(min_length=2, max_length=80)
    role: Literal["business_owner", "innovator", "investor", "admin"]
    browser: str = Field(min_length=2, max_length=120)
    consent_confirmed: Literal[True]
    tasks_attempted: int = Field(ge=1, le=100)
    tasks_without_help: int = Field(ge=0, le=100)
    investor_reviewed: int = Field(default=0, ge=0, le=5)
    investor_relevant: int = Field(default=0, ge=0, le=5)
    customer_reviewed: int = Field(default=0, ge=0, le=5)
    customer_relevant: int = Field(default=0, ge=0, le=5)
    assessments_reviewed: int = Field(default=0, ge=0, le=100)
    assessments_passed: int = Field(default=0, ge=0, le=100)
    clarity: int = Field(ge=1, le=5)
    usefulness: int = Field(ge=1, le=5)
    @model_validator(mode="after")
    def counts(self):
        for numerator, denominator in [("tasks_without_help", "tasks_attempted"), ("investor_relevant", "investor_reviewed"), ("customer_relevant", "customer_reviewed"), ("assessments_passed", "assessments_reviewed")]:
            if getattr(self, numerator) > getattr(self, denominator):
                raise ValueError("Successful counts cannot exceed the reviewed or attempted count.")
        return self
