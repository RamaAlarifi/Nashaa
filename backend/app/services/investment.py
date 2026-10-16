"""Investment settings, explained matches and explicit assessment grants."""
from fastapi import HTTPException
from sqlalchemy import select
from app.models.assessment import Assessment
from app.models.business_idea import BusinessIdea
from app.models.enums import AccountStatus, AssessmentStatus, IdeaVisibility, Role
from app.models.opportunities import AssessmentShare, InvestmentHistory, InvestorPreference, ProjectFundingRequirement
from app.models.user import User
from app.schemas.business_idea import BusinessIdeaSummary
from app.schemas.opportunities import SharedAssessmentOut
from app.services.matching import score
from app.services.opportunity_access import get, now, owned, participant, record, require, save
from app.industries import validate_industry


def preferences(db, user, payload):
    require(user, Role.INVESTOR)
    get(db, User, user.id, True)
    row = db.scalar(select(InvestorPreference).where(InvestorPreference.user_id == user.id)) or InvestorPreference(user_id=user.id)
    values = payload.model_dump(mode="json")
    values["industries"] = list(dict.fromkeys(validate_industry(v, v if v in (row.industries or []) else None, required=True) for v in values["industries"]))
    for key, value in values.items():
        setattr(row, key, value)
    return save(db, row)


def funding(db, user, idea_id, payload):
    require(user, Role.BUSINESS_OWNER)
    owned(get(db, BusinessIdea, idea_id, True), user)
    row = db.scalar(select(ProjectFundingRequirement).where(ProjectFundingRequirement.idea_id == idea_id)) or ProjectFundingRequirement(idea_id=idea_id)
    row.amount, row.currency = payload.amount, payload.currency
    return save(db, row)


def matches(db, user, idea_id=None):
    if idea_id:
        require(user, Role.BUSINESS_OWNER)
        ideas = [owned(get(db, BusinessIdea, idea_id), user)]
        prefs = list(db.scalars(select(InvestorPreference)))
    else:
        require(user, Role.INVESTOR)
        prefs = list(db.scalars(select(InvestorPreference).where(InvestorPreference.user_id == user.id)))
        ideas = list(db.scalars(select(BusinessIdea).join(User, User.id == BusinessIdea.owner_id).where(BusinessIdea.visibility == IdeaVisibility.REGISTERED, User.account_status == AccountStatus.ACTIVE)))
    result = []
    for pref in prefs:
        investor = db.get(User, pref.user_id)
        if not investor or investor.role != Role.INVESTOR or investor.account_status != AccountStatus.ACTIVE:
            continue
        history = list(db.scalars(select(InvestmentHistory).where(InvestmentHistory.user_id == pref.user_id)))
        for idea in ideas:
            money = db.scalar(select(ProjectFundingRequirement).where(ProjectFundingRequirement.idea_id == idea.id))
            match = score(idea, pref, money, history)
            if match:
                result.append({**match, "investor_id": investor.id, "investor_name": investor.profile.display_name,
                    "idea": BusinessIdeaSummary.model_validate(idea),
                    "history_sources": sorted({h.source for h in history})})
    return sorted(result, key=lambda x: (-x["score"], str(x["idea"].id), str(x["investor_id"])))


def share(db, user, idea_id, payload):
    require(user, Role.BUSINESS_OWNER)
    idea = owned(get(db, BusinessIdea, idea_id, True), user)
    investor = participant(db, payload.investor_id)
    require(investor, Role.INVESTOR)
    assessment = get(db, Assessment, payload.assessment_id)
    if idea.visibility != IdeaVisibility.REGISTERED:
        raise HTTPException(409, "Set the idea to registered visibility before approving assessment sharing.")
    if assessment.idea_id != idea.id or assessment.generation_status != AssessmentStatus.SUCCEEDED:
        raise HTTPException(422, "Select a successful assessment belonging to this idea.")
    row = db.scalar(select(AssessmentShare).where(AssessmentShare.assessment_id == assessment.id, AssessmentShare.investor_id == investor.id))
    if row is None:
        row = AssessmentShare(assessment_id=assessment.id, investor_id=investor.id, owner_id=user.id)
    row.revoked_at = None
    return save(db, row)


def revoke(db, user, share_id):
    row = owned(get(db, AssessmentShare, share_id), user)
    assessment = get(db, Assessment, row.assessment_id)
    owned(get(db, BusinessIdea, assessment.idea_id, True), user)
    row.revoked_at = now()
    return save(db, row)


def shared_view(db, user, share_id):
    require(user, Role.INVESTOR)
    row = owned(get(db, AssessmentShare, share_id), user, "investor_id")
    assessment = get(db, Assessment, row.assessment_id)
    idea = get(db, BusinessIdea, assessment.idea_id)
    owner = db.get(User, row.owner_id)
    if row.revoked_at or idea.visibility != IdeaVisibility.REGISTERED or not owner or owner.account_status != AccountStatus.ACTIVE or assessment.generation_status != AssessmentStatus.SUCCEEDED:
        raise HTTPException(404, "Shared assessment is unavailable.")
    return {"share_id": row.id, "idea": BusinessIdeaSummary.model_validate(idea),
        "assessment": SharedAssessmentOut.model_validate(assessment), "stale": assessment.idea_revision != idea.revision_number}


def revoke_idea_shares(db, idea_id):
    ids = select(Assessment.id).where(Assessment.idea_id == idea_id)
    for row in db.scalars(select(AssessmentShare).where(AssessmentShare.assessment_id.in_(ids), AssessmentShare.revoked_at.is_(None))):
        row.revoked_at = now()
