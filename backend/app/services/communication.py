"""Context-bound text conversations and current contact permissions (US14)."""
from fastapi import HTTPException
from sqlalchemy import or_, select
from app.models.business_idea import BusinessIdea
from app.models.enums import IdeaVisibility, Role
from app.models.opportunities import Challenge, ContactRequest, Conversation, Message, Proposal
from app.models.user import User
from app.services.opportunity_access import get, participant, save, verified


def context(db, sender, recipient, idea_id, challenge_id, lock=False):
    if sender.id == recipient.id:
        raise HTTPException(422, "Choose another participant.")
    if idea_id:
        item = get(db, BusinessIdea, idea_id, lock)
        owner = sender if sender.id == item.owner_id else recipient
        other = recipient if owner.id == sender.id else sender
        if owner.id != item.owner_id or owner.role != Role.BUSINESS_OWNER or other.role != Role.INVESTOR or item.visibility != IdeaVisibility.REGISTERED:
            raise HTTPException(403, "This idea does not permit contact between these participants.")
    else:
        item = get(db, Challenge, challenge_id, lock)
        owner = sender if sender.id == item.owner_id else recipient
        other = recipient if owner.id == sender.id else sender
        if owner.id != item.owner_id or owner.role != Role.BUSINESS_OWNER or other.role != Role.INNOVATOR:
            raise HTTPException(403, "This challenge does not permit contact between these participants.")
        if item.status != "published" and not db.scalar(select(Proposal).where(Proposal.challenge_id == item.id, Proposal.innovator_id == other.id)):
            raise HTTPException(403, "This challenge is unavailable for contact.")
    return owner, other


def eligible(*users):
    for user in users:
        verified(user)
        if not user.profile or user.profile.contact_preference == "closed":
            raise HTTPException(403, "Contact is currently closed for one of the participants.")


def thread(db, request):
    sender, recipient = participant(db, request.sender_id), participant(db, request.recipient_id)
    owner, other = context(db, sender, recipient, request.idea_id, request.challenge_id)
    query = select(Conversation).where(Conversation.owner_id == owner.id, Conversation.counterpart_id == other.id,
        Conversation.idea_id == request.idea_id, Conversation.challenge_id == request.challenge_id)
    row = db.scalar(query)
    if row is None:
        row = Conversation(owner_id=owner.id, counterpart_id=other.id, idea_id=request.idea_id, challenge_id=request.challenge_id)
        db.add(row)
    row.current_contact_request_id = request.id
    return row


def request_contact(db, user, payload):
    recipient = participant(db, payload.recipient_id)
    context(db, user, recipient, payload.idea_id, payload.challenge_id, True)
    # Stable lock order also serialises contact preference and permission changes.
    users = {str(x): get(db, User, x, True) for x in sorted([user.id, recipient.id], key=str)}
    user, recipient = users[str(user.id)], users[str(recipient.id)]
    eligible(user, recipient)
    existing = db.scalar(select(ContactRequest).where(
        or_((ContactRequest.sender_id == user.id) & (ContactRequest.recipient_id == recipient.id),
            (ContactRequest.sender_id == recipient.id) & (ContactRequest.recipient_id == user.id)),
        ContactRequest.idea_id == payload.idea_id, ContactRequest.challenge_id == payload.challenge_id,
        ContactRequest.status.in_(["pending", "accepted"])))
    if existing:
        raise HTTPException(409, "A pending or accepted contact permission already exists for this context.")
    row = ContactRequest(sender_id=user.id, **payload.model_dump(), status="accepted" if recipient.profile.contact_preference == "open" else "pending")
    db.add(row)
    db.flush()
    if row.status == "accepted":
        thread(db, row)
    return save(db, row)


def decide_contact(db, user, request_id, decision):
    row = get(db, ContactRequest, request_id)
    sender, recipient = participant(db, row.sender_id), participant(db, row.recipient_id)
    context(db, sender, recipient, row.idea_id, row.challenge_id, True)
    row = get(db, ContactRequest, request_id, True)
    if user.id not in (row.sender_id, row.recipient_id):
        raise HTTPException(404, "Contact request not found.")
    if decision == "revoked":
        if row.status not in ("accepted", "pending"):
            raise HTTPException(409, "This permission is already inactive.")
    elif user.id != row.recipient_id or row.status != "pending":
        raise HTTPException(403, "Only the recipient can decide a pending request.")
    if decision == "accepted":
        eligible(sender, recipient)
        thread(db, row)
    row.status = decision
    return save(db, row)


def authorised_thread(db, user, conversation_id, lock=False):
    row = get(db, Conversation, conversation_id)
    if user.id not in (row.owner_id, row.counterpart_id):
        raise HTTPException(404, "Conversation not found.")
    owner, other = participant(db, row.owner_id), participant(db, row.counterpart_id)
    context(db, owner, other, row.idea_id, row.challenge_id, lock)
    if lock:
        row = get(db, Conversation, conversation_id, True)
    eligible(owner, other)
    permission = db.get(ContactRequest, row.current_contact_request_id) if row.current_contact_request_id else None
    if not permission or permission.status != "accepted":
        raise HTTPException(403, "Contact permission is no longer active.")
    return row


def send(db, user, conversation_id, payload):
    row = authorised_thread(db, user, conversation_id, True)
    from app.services.opportunity_access import now
    row.updated_at = now()
    return save(db, Message(conversation_id=row.id, sender_id=user.id, body=payload.body))
