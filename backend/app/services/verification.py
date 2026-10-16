"""Platform verification only; no claim of official identity validation (US13)."""
from fastapi import HTTPException
from sqlalchemy import select
from app.models.enums import Role
from app.models.opportunities import VerificationRequest
from app.models.user import User
from app.services.opportunity_access import get, now, require, save


def request_verification(db, user, payload):
    require(user, Role.BUSINESS_OWNER, Role.INNOVATOR, Role.INVESTOR)
    user = get(db, User, user.id, True)
    if user.verification_status in ("approved", "pending"):
        raise HTTPException(409, "Your account is already approved or has a pending request.")
    user.verification_status = "pending"
    return save(db, VerificationRequest(user_id=user.id, **payload.model_dump()))


def decide(db, user, request_id, payload):
    require(user, Role.ADMIN)
    row = get(db, VerificationRequest, request_id, True)
    if row.user_id == user.id or row.status != "pending":
        raise HTTPException(409, "This request cannot be reviewed.")
    applicant = get(db, User, row.user_id, True)
    row.status = applicant.verification_status = payload.decision
    row.decision_reason, row.reviewer_id, row.decided_at = payload.reason, user.id, now()
    return save(db, row)
