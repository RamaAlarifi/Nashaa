"""Challenge lifecycle and atomic collaborator selection (US09–US12)."""
from fastapi import HTTPException
from sqlalchemy import select
from app.models.business_idea import BusinessIdea
from app.models.enums import AccountStatus, Role
from app.models.opportunities import Challenge, Collaboration, Proposal
from app.models.user import User
from app.services.opportunity_access import get, now, owned, require, save, verified
from app.industries import validate_industry


def write_challenge(db, user, payload, challenge_id=None):
    require(user, Role.BUSINESS_OWNER)
    row = owned(get(db, Challenge, challenge_id, True), user) if challenge_id else Challenge(owner_id=user.id)
    if challenge_id and (row.status == "closed" or db.scalar(select(Collaboration).where(Collaboration.challenge_id == row.id))):
        raise HTTPException(409, "A closed or selected challenge cannot be edited.")
    if challenge_id and db.scalar(select(Proposal).where(Proposal.challenge_id == row.id)):
        raise HTTPException(409, "Challenges with proposals cannot be changed. Close this challenge and create a new draft.")
    if payload.idea_id:
        owned(get(db, BusinessIdea, payload.idea_id), user)
    values = payload.model_dump()
    values["industry"] = validate_industry(values["industry"], row.industry if challenge_id else None)
    for key, value in values.items():
        setattr(row, key, value)
    row.status, row.approved_at = "draft", None
    return save(db, row)


def publish(db, user, challenge_id):
    require(user, Role.BUSINESS_OWNER)
    row = owned(get(db, Challenge, challenge_id, True), user)
    if row.status != "draft":
        raise HTTPException(409, "Only a draft can be published.")
    if not all((row.problem.strip(), row.desired_outcome.strip(), row.required_skills, row.industry.strip(), row.timeline.strip())):
        raise HTTPException(422, "Add the problem, desired outcome, skills, industry and timeline before approving publication.")
    row.status, row.approved_at = "published", now()
    return save(db, row)


def close(db, user, challenge_id):
    require(user, Role.BUSINESS_OWNER)
    row = owned(get(db, Challenge, challenge_id, True), user)
    row.status = "closed"
    return save(db, row)


def visible_challenge(db, user, challenge_id):
    row = get(db, Challenge, challenge_id)
    if row.owner_id != user.id and get(db, User, row.owner_id).account_status != AccountStatus.ACTIVE:
        raise HTTPException(404, "Challenge not found.")
    if row.owner_id != user.id and row.status != "published":
        # An innovator retains access to the context of their submitted work.
        if not db.scalar(select(Proposal).where(Proposal.challenge_id == row.id, Proposal.innovator_id == user.id)):
            raise HTTPException(404, "Challenge not found.")
    return row


def submit(db, user, challenge_id, payload):
    require(user, Role.INNOVATOR)
    # The shared challenge lock serialises submission, selection and closing.
    row = get(db, Challenge, challenge_id, True)
    verified(get(db, User, user.id, True))
    owner = get(db, User, row.owner_id)
    if owner.account_status != AccountStatus.ACTIVE or row.status != "published" or db.scalar(select(Collaboration).where(Collaboration.challenge_id == row.id)):
        raise HTTPException(409, "This challenge is no longer accepting proposals.")
    return save(db, Proposal(challenge_id=row.id, innovator_id=user.id, **payload.model_dump()))


def select_proposal(db, user, challenge_id, proposal_id):
    require(user, Role.BUSINESS_OWNER)
    challenge = owned(get(db, Challenge, challenge_id, True), user)
    if challenge.status != "published" or db.scalar(select(Collaboration).where(Collaboration.challenge_id == challenge.id)):
        raise HTTPException(409, "This challenge is closed or already has a selected collaborator.")
    proposal = get(db, Proposal, proposal_id)
    if proposal.challenge_id != challenge.id:
        raise HTTPException(404, "Proposal not found for this challenge.")
    verified(get(db, User, proposal.innovator_id, True))
    for row in db.scalars(select(Proposal).where(Proposal.challenge_id == challenge.id)):
        row.status = "selected" if row.id == proposal.id else "not_selected"
    challenge.status = "closed"
    return save(db, Collaboration(challenge_id=challenge.id, selected_proposal_id=proposal.id))
