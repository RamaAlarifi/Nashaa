"""Sprint 2 routes. Permissions remain enforced for direct API requests."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.database import get_db
from app.models.assessment import Assessment
from app.models.business_idea import BusinessIdea
from app.models.enums import AccountStatus, AssessmentStatus, Role
from app.models.opportunities import AssessmentShare, Challenge, ContactRequest, Conversation, InvestmentHistory, InvestorPreference, Message, ProjectFundingRequirement, Proposal, VerificationRequest
from app.models.user import User
from app.schemas.opportunities import ChallengeIn, ContactDecisionIn, ContactIn, ContactPreferenceIn, DecisionIn, FundingIn, HistoryIn, MessageIn, PreferenceIn, ProposalIn, PublishIn, ShareIn, SharedAssessmentOut, VerificationIn
from app.services import challenges, communication, investment, verification
from app.services.opportunity_access import get, owned, record, require, save
from app.industries import matches_filter, validate_industry

router = APIRouter(prefix="/api", tags=["Sprint 2"])
DB = Depends(get_db)
AUTH = Depends(get_current_user)


@router.get("/verification")
def verification_status(db: Session = DB, user: User = AUTH):
    return {"status": user.verification_status, "requests": [record(r) for r in db.scalars(select(VerificationRequest).where(VerificationRequest.user_id == user.id).order_by(VerificationRequest.created_at.desc()))]}


@router.post("/verification", status_code=201)
def request_verification(payload: VerificationIn, db: Session = DB, user: User = AUTH):
    return record(verification.request_verification(db, user, payload))


@router.get("/admin/verification")
def review_queue(db: Session = DB, user: User = AUTH):
    require(user, Role.ADMIN)
    return [{**record(r), "applicant_name": get(db, User, r.user_id).profile.display_name} for r in db.scalars(select(VerificationRequest).order_by(VerificationRequest.created_at.desc()))]


@router.post("/admin/verification/{request_id}/decision")
def review_request(request_id: UUID, payload: DecisionIn, db: Session = DB, user: User = AUTH):
    return record(verification.decide(db, user, request_id, payload))


@router.get("/challenges")
def list_challenges(q: str = Query("", max_length=200), industry: str = Query("", max_length=120), location: str = Query("", max_length=120), skill: str = Query("", max_length=120), mine: bool = False, db: Session = DB, user: User = AUTH):
    require(user, Role.BUSINESS_OWNER, Role.INNOVATOR)
    query = select(Challenge)
    if mine:
        require(user, Role.BUSINESS_OWNER)
        query = query.where(Challenge.owner_id == user.id)
    else:
        query = query.join(User, User.id == Challenge.owner_id).where(Challenge.status == "published", User.account_status == AccountStatus.ACTIVE)
    rows = list(db.scalars(query.order_by(Challenge.created_at.desc())))
    return [record(r) for r in rows if q.casefold() in (r.title + " " + r.problem).casefold() and matches_filter(industry, r.industry) and location.casefold() in r.location.casefold() and (not skill or any(skill.casefold() in s.casefold() for s in r.required_skills))]


@router.post("/challenges", status_code=201)
def create_challenge(payload: ChallengeIn, db: Session = DB, user: User = AUTH):
    return record(challenges.write_challenge(db, user, payload))


@router.get("/challenges/{challenge_id}")
def challenge_details(challenge_id: UUID, db: Session = DB, user: User = AUTH):
    require(user, Role.BUSINESS_OWNER, Role.INNOVATOR)
    return record(challenges.visible_challenge(db, user, challenge_id))


@router.put("/challenges/{challenge_id}")
def edit_challenge(challenge_id: UUID, payload: ChallengeIn, db: Session = DB, user: User = AUTH):
    return record(challenges.write_challenge(db, user, payload, challenge_id))


@router.post("/challenges/{challenge_id}/publish")
def publish_challenge(challenge_id: UUID, payload: PublishIn, db: Session = DB, user: User = AUTH):
    return record(challenges.publish(db, user, challenge_id))


@router.post("/challenges/{challenge_id}/close")
def close_challenge(challenge_id: UUID, db: Session = DB, user: User = AUTH):
    return record(challenges.close(db, user, challenge_id))


@router.post("/challenges/{challenge_id}/proposals", status_code=201)
def submit_proposal(challenge_id: UUID, payload: ProposalIn, db: Session = DB, user: User = AUTH):
    return record(challenges.submit(db, user, challenge_id, payload))


@router.get("/proposals")
def own_proposals(db: Session = DB, user: User = AUTH):
    require(user, Role.INNOVATOR)
    return [{**record(r), "challenge_title": get(db, Challenge, r.challenge_id).title} for r in db.scalars(select(Proposal).where(Proposal.innovator_id == user.id).order_by(Proposal.created_at.desc()))]


@router.get("/challenges/{challenge_id}/proposals")
def proposal_comparison(challenge_id: UUID, db: Session = DB, user: User = AUTH):
    owned(get(db, Challenge, challenge_id), user)
    return [{**record(r), "innovator_name": get(db, User, r.innovator_id).profile.display_name} for r in db.scalars(select(Proposal).where(Proposal.challenge_id == challenge_id).order_by(Proposal.created_at))]


@router.post("/challenges/{challenge_id}/select/{proposal_id}", status_code=201)
def choose_proposal(challenge_id: UUID, proposal_id: UUID, db: Session = DB, user: User = AUTH):
    return record(challenges.select_proposal(db, user, challenge_id, proposal_id))


@router.get("/contact-preference")
def contact_preference(user: User = AUTH):
    return {"preference": user.profile.contact_preference}


@router.put("/contact-preference")
def update_contact(payload: ContactPreferenceIn, db: Session = DB, user: User = AUTH):
    require(user, Role.BUSINESS_OWNER, Role.INNOVATOR, Role.INVESTOR)
    user = get(db, User, user.id, True)
    user.profile.contact_preference = payload.preference
    save(db, user.profile)
    return {"preference": payload.preference}


@router.get("/contact-requests")
def contacts(db: Session = DB, user: User = AUTH):
    result = []
    for row in db.scalars(select(ContactRequest).where(or_(ContactRequest.sender_id == user.id, ContactRequest.recipient_id == user.id)).order_by(ContactRequest.created_at.desc())):
        other = get(db, User, row.recipient_id if row.sender_id == user.id else row.sender_id)
        context = get(db, BusinessIdea if row.idea_id else Challenge, row.idea_id or row.challenge_id)
        result.append({**record(row), "participant_name": other.profile.display_name,
            "context_title": context.name if row.idea_id else context.title})
    return result


@router.post("/contact-requests", status_code=201)
def create_contact(payload: ContactIn, db: Session = DB, user: User = AUTH):
    return record(communication.request_contact(db, user, payload))


@router.post("/contact-requests/{request_id}/decision")
def decide_contact(request_id: UUID, payload: ContactDecisionIn, db: Session = DB, user: User = AUTH):
    return record(communication.decide_contact(db, user, request_id, payload.decision))


@router.get("/conversations")
def conversations(db: Session = DB, user: User = AUTH):
    rows = db.scalars(select(Conversation).where(or_(Conversation.owner_id == user.id, Conversation.counterpart_id == user.id)).order_by(Conversation.updated_at.desc()))
    result = []
    for row in rows:
        other = get(db, User, row.counterpart_id if row.owner_id == user.id else row.owner_id)
        result.append({**record(row), "participant_name": other.profile.display_name,
            "context_title": get(db, BusinessIdea if row.idea_id else Challenge, row.idea_id or row.challenge_id).name if row.idea_id else get(db, Challenge, row.challenge_id).title})
    return result


@router.get("/conversations/{conversation_id}/messages")
def messages(conversation_id: UUID, db: Session = DB, user: User = AUTH):
    communication.authorised_thread(db, user, conversation_id)
    return [record(r) for r in db.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at, Message.id))]


@router.post("/conversations/{conversation_id}/messages", status_code=201)
def send_message(conversation_id: UUID, payload: MessageIn, db: Session = DB, user: User = AUTH):
    return record(communication.send(db, user, conversation_id, payload))


@router.get("/investor-preferences")
def get_preferences(db: Session = DB, user: User = AUTH):
    require(user, Role.INVESTOR)
    row = db.scalar(select(InvestorPreference).where(InvestorPreference.user_id == user.id))
    return record(row) if row else None


@router.get("/investors")
def participating_investors(db: Session = DB, user: User = AUTH):
    require(user, Role.BUSINESS_OWNER)
    return [{"id": r.id, "name": r.profile.display_name} for r in db.scalars(select(User).join(InvestorPreference, InvestorPreference.user_id == User.id).where(User.role == Role.INVESTOR, User.account_status == AccountStatus.ACTIVE).order_by(User.id))]


@router.put("/investor-preferences")
def put_preferences(payload: PreferenceIn, db: Session = DB, user: User = AUTH):
    return record(investment.preferences(db, user, payload))


@router.get("/investment-history")
def investment_history(db: Session = DB, user: User = AUTH):
    require(user, Role.INVESTOR)
    return [record(r) for r in db.scalars(select(InvestmentHistory).where(InvestmentHistory.user_id == user.id).order_by(InvestmentHistory.created_at.desc()))]


@router.post("/investment-history", status_code=201)
def add_history(payload: HistoryIn, db: Session = DB, user: User = AUTH):
    require(user, Role.INVESTOR)
    values = payload.model_dump(mode="json")
    values["industry"] = validate_industry(values["industry"], required=True)
    return record(save(db, InvestmentHistory(user_id=user.id, **values)))


@router.put("/investment-history/{history_id}")
def edit_history(history_id: UUID, payload: HistoryIn, db: Session = DB, user: User = AUTH):
    require(user, Role.INVESTOR)
    row = owned(get(db, InvestmentHistory, history_id), user, "user_id")
    values = payload.model_dump(mode="json")
    values["industry"] = validate_industry(values["industry"], row.industry, required=True)
    for key, value in values.items():
        setattr(row, key, value)
    return record(save(db, row))


@router.delete("/investment-history/{history_id}", status_code=204)
def remove_history(history_id: UUID, db: Session = DB, user: User = AUTH):
    require(user, Role.INVESTOR)
    db.delete(owned(get(db, InvestmentHistory, history_id), user, "user_id"))
    db.commit()


@router.get("/ideas/{idea_id}/funding")
def get_funding(idea_id: UUID, db: Session = DB, user: User = AUTH):
    owned(get(db, BusinessIdea, idea_id), user)
    row = db.scalar(select(ProjectFundingRequirement).where(ProjectFundingRequirement.idea_id == idea_id))
    return record(row) if row else None


@router.put("/ideas/{idea_id}/funding")
def put_funding(idea_id: UUID, payload: FundingIn, db: Session = DB, user: User = AUTH):
    return record(investment.funding(db, user, idea_id, payload))


@router.get("/ideas/{idea_id}/investor-matches")
def investor_matches(idea_id: UUID, db: Session = DB, user: User = AUTH):
    return investment.matches(db, user, idea_id)


@router.get("/investor/projects")
def project_feed(db: Session = DB, user: User = AUTH):
    return investment.matches(db, user)


@router.get("/ideas/{idea_id}/assessment-shares")
def owner_shares(idea_id: UUID, db: Session = DB, user: User = AUTH):
    owned(get(db, BusinessIdea, idea_id), user)
    return [{**record(r), "investor_name": get(db, User, r.investor_id).profile.display_name} for r in db.scalars(select(AssessmentShare).join(Assessment, Assessment.id == AssessmentShare.assessment_id).where(Assessment.idea_id == idea_id))]


@router.get("/ideas/{idea_id}/assessment-versions", response_model=list[SharedAssessmentOut])
def assessment_versions(idea_id: UUID, db: Session = DB, user: User = AUTH):
    owned(get(db, BusinessIdea, idea_id), user)
    return list(db.scalars(select(Assessment).where(Assessment.idea_id == idea_id, Assessment.generation_status == AssessmentStatus.SUCCEEDED).order_by(Assessment.seq.desc())))


@router.post("/ideas/{idea_id}/assessment-shares", status_code=201)
def approve_share(idea_id: UUID, payload: ShareIn, db: Session = DB, user: User = AUTH):
    return record(investment.share(db, user, idea_id, payload))


@router.delete("/assessment-shares/{share_id}")
def revoke_share(share_id: UUID, db: Session = DB, user: User = AUTH):
    return record(investment.revoke(db, user, share_id))


@router.get("/assessment-shares")
def investor_shares(db: Session = DB, user: User = AUTH):
    require(user, Role.INVESTOR)
    result = []
    for row in db.scalars(select(AssessmentShare).where(AssessmentShare.investor_id == user.id, AssessmentShare.revoked_at.is_(None))):
        try:
            result.append(investment.shared_view(db, user, row.id))
        except HTTPException as exc:
            if exc.status_code != 404:
                raise
    return result


@router.get("/assessment-shares/{share_id}")
def shared_assessment(share_id: UUID, db: Session = DB, user: User = AUTH):
    return investment.shared_view(db, user, share_id)
