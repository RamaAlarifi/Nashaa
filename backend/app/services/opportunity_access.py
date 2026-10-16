"""Shared Sprint 2 permission and persistence helpers."""
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.enums import AccountStatus, Role
from app.models.user import User


def now():
    return datetime.now(timezone.utc)


def require(user, *roles):
    if user.role not in roles:
        raise HTTPException(403, "This action is not available for your role.")


def verified(user):
    if user.account_status != AccountStatus.ACTIVE or user.verification_status != "approved":
        raise HTTPException(403, "Approved account verification is required.")


def get(db, model, record_id, lock=False):
    query = select(model).where(model.id == record_id).execution_options(populate_existing=True)
    row = db.scalar(query.with_for_update() if lock else query)
    if row is None:
        raise HTTPException(404, "Record not found.")
    return row


def owned(row, user, field="owner_id"):
    if getattr(row, field) != user.id:
        raise HTTPException(404, "Record not found.")
    return row


def save(db, row):
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "This action conflicts with an existing record. Refresh and try again.")
    db.refresh(row)
    return row


def record(row):
    """Use only on the explicitly scoped opportunity models, never on User."""
    values = {column.name: getattr(row, column.name) for column in row.__table__.columns}
    # Preserve exact monetary values and match the frontend's string contracts.
    return {key: format(value, "f") if isinstance(value, Decimal) else value for key, value in values.items()}


def participant(db, user_id):
    user = get(db, User, user_id)
    require(user, Role.BUSINESS_OWNER, Role.INNOVATOR, Role.INVESTOR)
    if user.account_status != AccountStatus.ACTIVE:
        raise HTTPException(403, "This participant is unavailable.")
    return user
