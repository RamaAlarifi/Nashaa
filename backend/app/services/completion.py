"""Sprint 3 lifecycle, permitted discovery, private follow-up and moderation."""
import csv
import hashlib
import io
import re
from urllib.parse import urlsplit
from fastapi import HTTPException
from sqlalchemy import select, func, delete
from app.ai.base import AIServiceError
from app.ai.discovery import generate_fields
from app.models.completion import ProgressUpdate, CustomerProfile, LeadSource, CompanyRecord, Lead, LeadNote, OutreachDraft, Rating, UserReport, AdminAction, EvaluationSession
from app.models.business_idea import BusinessIdea
from app.models.opportunities import Collaboration, Challenge, Proposal, Message, Conversation
from app.models.user import User
from app.models.session import Session as LoginSession
from app.models.enums import Role, IdeaVisibility, AccountStatus
from app.schemas.completion import ProfileDetails
from app.services.opportunity_access import get, owned, require, record, save, now
from app.services import challenges, communication, business_ideas, investment
from app.services.assessment import _idea_to_input
from app.industries import validate_industry, CATALOG
from app.services.errors import IdeaNotFound, VisibilityBlocked


def collaboration(db, user, identifier, lock=False):
    require(user, Role.BUSINESS_OWNER, Role.INNOVATOR)
    row = get(db, Collaboration, identifier, lock)
    challenge = get(db, Challenge, row.challenge_id)
    proposal = get(db, Proposal, row.selected_proposal_id)
    if user.id not in (challenge.owner_id, proposal.innovator_id):
        raise HTTPException(404, "Collaboration not found.")
    return row, challenge, proposal


def collaborations(db, user):
    require(user, Role.BUSINESS_OWNER, Role.INNOVATOR)
    rows = db.scalars(select(Collaboration).join(Challenge, Challenge.id == Collaboration.challenge_id).join(Proposal, Proposal.id == Collaboration.selected_proposal_id).where((Challenge.owner_id == user.id) | (Proposal.innovator_id == user.id)).order_by(Collaboration.updated_at.desc()))
    return [{**record(r), "challenge_title":get(db, Challenge, r.challenge_id).title} for r in rows]


def collaboration_view(db, user, identifier):
    row, challenge, proposal = collaboration(db, user, identifier)
    return {**record(row), "challenge_title":challenge.title, "owner_id":challenge.owner_id, "innovator_id":proposal.innovator_id,
        "updates":[record(r) for r in db.scalars(select(ProgressUpdate).where(ProgressUpdate.collaboration_id == row.id).order_by(ProgressUpdate.created_at))],
        "ratings":[record(r) for r in db.scalars(select(Rating).where(Rating.collaboration_id == row.id))]}


def progress(db, user, identifier, body):
    row, _, _ = collaboration(db, user, identifier, True)
    if row.status == "completed":
        raise HTTPException(409, "Completed work cannot receive more progress updates.")
    return save(db, ProgressUpdate(collaboration_id=row.id, author_id=user.id, body=body))


def transition(db, user, identifier, action):
    row, challenge, proposal = collaboration(db, user, identifier, True)
    if action == "ready":
        if user.id != proposal.innovator_id:
            raise HTTPException(403, "Only the selected innovator can mark work ready.")
        if row.status != "active":
            raise HTTPException(409, "Only active work can be marked ready.")
        row.status, row.ready_at = "ready", now()
    else:
        if user.id != challenge.owner_id:
            raise HTTPException(403, "Only the owner can confirm completion.")
        if row.status != "ready":
            raise HTTPException(409, "The innovator must mark the work ready first.")
        row.status, row.completed_at = "completed", now()
    return save(db, row)


def rate(db, user, identifier, payload):
    row, challenge, proposal = collaboration(db, user, identifier, True)
    if row.status != "completed":
        raise HTTPException(409, "Ratings require a completed collaboration.")
    return save(db, Rating(collaboration_id=row.id, author_id=user.id, recipient_id=proposal.innovator_id if user.id == challenge.owner_id else challenge.owner_id, **payload.model_dump()))


def owner_idea(db, user, identifier, lock=False):
    require(user, Role.BUSINESS_OWNER)
    return owned(get(db, BusinessIdea, identifier, lock), user)


def profile(db, user, identifier):
    owner_idea(db, user, identifier)
    return db.scalar(select(CustomerProfile).where(CustomerProfile.idea_id == identifier))


def write_profile(db, user, identifier, payload=None, kind=None):
    idea = owner_idea(db, user, identifier, True)
    if payload:
        details, kind, provider = payload.details.model_dump(), payload.kind, "owner_edited"
    else:
        # Release the transaction during generation; recheck revision under lock
        # before saving so a stale response cannot overwrite a concurrent edit.
        revision = idea.revision_number
        existing = db.scalar(select(CustomerProfile).where(CustomerProfile.idea_id == identifier))
        expected_update = (existing.updated_at, existing.kind, dict(existing.details)) if existing else None
        context = _idea_to_input(idea).model_dump(mode="json")
        context["customer_focus"] = kind
        context["industry_categories"] = [{"id":code,"label":label} for code,label,_ in CATALOG]
        db.commit()
        fields = list(ProfileDetails.model_fields)
        simulated = {"customer_type":context['intended_customers'] or "Customer segment not specified", "industry":context['industry'], "location":context['target_location'], "size":"Not supplied", "main_need":context['problem'], "buying_motivation":"Assess whether the submitted solution addresses the stated need: " + context['solution'], "objections":"Pricing and adoption evidence have not been supplied.", "channels":"Test a suitable opt-in channel with the stated segment; channel fit is unvalidated.", "assumptions":"Simulated demonstration suggestion using owner input; no external validation."}
        try:
            details, provider = generate_fields("Suggest an editable target-customer profile for the explicitly selected business or consumer focus. Target-customer industry may differ from the business industry: choose a supported identifier from industry_categories only when the submitted customer context supports it; otherwise leave industry empty. Leave unknown location empty, describe other unknowns plainly, and label inferred segment choices as hypotheses. Do not provide personal contacts.", context, fields, simulated)
            details = ProfileDetails.model_validate(details).model_dump()
        except (AIServiceError, ValueError):
            raise HTTPException(503, "Customer-profile generation failed. Please retry. The previous profile remains saved.")
        idea = owner_idea(db, user, identifier, True)
        current = db.scalar(select(CustomerProfile).where(CustomerProfile.idea_id == identifier).execution_options(populate_existing=True))
        if idea.revision_number != revision or ((current.updated_at, current.kind, dict(current.details)) if current else None) != expected_update:
            raise HTTPException(409, "The idea or customer profile changed during generation. Retry using the latest information.")
    details['industry'] = validate_industry(details['industry'])
    row = db.scalar(select(CustomerProfile).where(CustomerProfile.idea_id == identifier)) or CustomerProfile(idea_id=identifier)
    row.details, row.kind, row.provider, row.idea_revision = details, kind, provider, idea.revision_number
    return save(db, row)


def parse_companies(payload):
    if len(payload.csv_text.encode('utf-8')) > 100000:
        raise HTTPException(422, "CSV files must be at most 100 KB.")
    try:
        reader = csv.DictReader(io.StringIO(payload.csv_text.lstrip('\ufeff')), strict=True)
        fields = reader.fieldnames
        required = {'company_name', 'industry', 'location', 'website', 'business_need'}
        if not fields or len(fields) != len(set(fields)) or set(fields) != required:
            raise ValueError("Use exactly these CSV headers: company_name,industry,location,website,business_need. Personal-contact columns are not accepted.")
        rows = []
        for index, raw in enumerate(reader, 2):
            if index > 201:
                raise ValueError("Import at most 200 company records at once.")
            if None in raw or any(v is None for v in raw.values()):
                raise ValueError(f"Row {index} does not match the required columns.")
            item = {k:v.strip() for k,v in raw.items()}
            if not item['company_name'] or any(len(v)>limit for v,limit in [(item['company_name'],200),(item['industry'],120),(item['location'],120),(item['website'],500),(item['business_need'],2000)]):
                raise ValueError(f"Row {index} has missing or oversized values.")
            if any(re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',v) or v.startswith(('=','+','-','@')) for v in item.values()):
                raise ValueError(f"Row {index} contains unsafe control or spreadsheet formula content.")
            if item['website']:
                url = urlsplit(item['website'])
                if url.scheme not in ('http','https') or not url.hostname or url.username or url.password:
                    raise ValueError(f"Row {index} must use a public company website URL or leave it blank.")
            item['industry'] = validate_industry(item['industry'])
            # Match name and location even when repeated imports omit/change a URL.
            item['fingerprint'] = hashlib.sha256((item['company_name'].casefold()+'|'+item['location'].casefold()).encode()).hexdigest()
            rows.append(item)
        if not rows:
            raise ValueError("The CSV contains no company records.")
        return rows
    except (ValueError, csv.Error, UnicodeError) as exc:
        raise HTTPException(422, str(exc))


def import_companies(db, user, identifier, payload):
    rows = parse_companies(payload)  # validate the entire file before saving anything
    owner_idea(db, user, identifier, True)
    cp = profile(db, user, identifier)
    if not cp or cp.kind != 'business':
        raise HTTPException(409, "Save a business-customer profile before importing company records.")
    source = LeadSource(owner_id=user.id, idea_id=identifier, name=payload.source, filename=payload.filename, permission="Owner confirmed permission to use these company records", fictional=payload.fictional)
    db.add(source); db.flush()
    existing = set(db.scalars(select(CompanyRecord.fingerprint).where(CompanyRecord.idea_id == identifier)))
    inserted = 0
    for item in rows:
        if item['fingerprint'] in existing:
            continue
        existing.add(item['fingerprint']); inserted += 1
        db.add(CompanyRecord(idea_id=identifier, source_id=source.id, name=item['company_name'], **{k:v for k,v in item.items() if k != 'company_name'}))
    db.commit()
    return {"imported":inserted, "duplicates_skipped":len(rows)-inserted, "source":record(source)}


def customer_suggestions(db, user, identifier):
    cp = profile(db, user, identifier)
    if not cp:
        return {"kind":None, "items":[], "message":"Generate or save a customer profile first."}
    if cp.kind == 'consumer':
        return {"kind":"consumer", "items":[], "segments":[cp.details['customer_type']], "channels":cp.details['channels'], "need":cp.details['main_need'], "assumptions":cp.details['assumptions'], "message":"Segment hypotheses from your saved profile, not personal leads or verified demand."}
    items = []
    for company in db.scalars(select(CompanyRecord).where(CompanyRecord.idea_id == identifier)):
        reasons, missing, score = [], [], 0
        for key,weight in [('industry',50),('location',30)]:
            expected, actual = cp.details.get(key,''), getattr(company,key)
            if not expected or not actual:
                missing.append(f"{key.title()} not specified for comparison")
            elif expected.casefold() == actual.casefold():
                score += weight; reasons.append(f"{key.title()} matches the saved customer profile")
        tokens = set(re.findall(r'\w{4,}',cp.details['main_need'].casefold()))
        if tokens & set(re.findall(r'\w{4,}',company.business_need.casefold())):
            score += 20; reasons.append("Stated business need shares terms with your target need")
        if score:
            source = get(db, LeadSource, company.source_id)
            items.append({**record(company),"score":score,"reasons":reasons,"missing":missing,"source":source.name,"fictional":source.fictional})
    return {"kind":"business", "items":sorted(items,key=lambda r:(-r['score'],r['name'].casefold(),str(r['id'])))[:50], "message":"Matches use your saved customer profile and permission-confirmed imports. Scores are fit indicators, not verified demand." if items else "No matching permitted company records. Import a valid company CSV or refine the customer profile."}


def save_lead(db, user, identifier, payload):
    idea = owner_idea(db, user, identifier, True)
    previous = db.scalar(select(Lead).where(Lead.owner_id == user.id, Lead.idea_id == identifier, Lead.kind == payload.kind, Lead.reference_id == payload.reference_id))
    if previous:
        return previous
    if payload.kind == 'customer':
        cp = profile(db, user, identifier)
        company = get(db, CompanyRecord, payload.reference_id)
        if not cp or cp.kind != 'business' or company.idea_id != identifier:
            raise HTTPException(404, "Company record not available for this business-customer profile.")
        source = get(db, LeadSource, company.source_id)
        snapshot = {"name":company.name,"industry":company.industry,"location":company.location,"website":company.website,"business_need":company.business_need,"source":source.name,"fictional":source.fictional}
    else:
        investor = get(db, User, payload.reference_id)
        if investor.role != Role.INVESTOR or investor.account_status != AccountStatus.ACTIVE or not any(m['investor_id'] == investor.id for m in investment.matches(db, user, idea.id)):
            raise HTTPException(404, "Choose an available suggested investor for this idea.")
        snapshot = {"name":investor.profile.display_name,"source":"Registered Nashaa investor profile; compatibility is not investment advice"}
    return save(db, Lead(owner_id=user.id, idea_id=identifier, kind=payload.kind, reference_id=payload.reference_id, snapshot=snapshot))


def lead_view(db, user, identifier):
    require(user, Role.BUSINESS_OWNER)
    row = owned(get(db, Lead, identifier), user)
    return {**record(row),"notes":[record(n) for n in db.scalars(select(LeadNote).where(LeadNote.lead_id == row.id).order_by(LeadNote.created_at))],"draft":record(d) if (d:=db.scalar(select(OutreachDraft).where(OutreachDraft.lead_id == row.id))) else None}


def draft(db, user, identifier, body=None):
    require(user, Role.BUSINESS_OWNER)
    lead = owned(get(db, Lead, identifier, True), user)
    idea = owner_idea(db, user, lead.idea_id)
    existing = db.scalar(select(OutreachDraft).where(OutreachDraft.lead_id == lead.id))
    expected = (existing.updated_at, existing.body, existing.provider) if existing else None
    revision = idea.revision_number
    if body is None:
        context={"business":_idea_to_input(idea).model_dump(mode='json'),"selected_lead":lead.snapshot}
        simulated={"body":f"Hello {lead.snapshot['name']},\nI am developing {idea.name}. {idea.solution}\nI would welcome a short discussion about whether this addresses your needs.\nThis is an editable simulated draft; review all claims before use."}
        db.commit()
        try:
            result, provider = generate_fields("Write one editable outreach draft of at most 250 words using the selected prospect and business. Do not imply established relationships, traction or claims absent from context. Do not send anything.",context,['body'],simulated)
            body = result['body']
        except AIServiceError:
            raise HTTPException(503,"Outreach generation failed. Retry later. Your lead, notes and previous draft remain saved.")
        lead = owned(get(db, Lead, identifier, True), user)
        idea = owner_idea(db, user, lead.idea_id)
        current = db.scalar(select(OutreachDraft).where(OutreachDraft.lead_id == lead.id).execution_options(populate_existing=True))
        if idea.revision_number != revision or ((current.updated_at, current.body, current.provider) if current else None) != expected:
            raise HTTPException(409,"The business or draft changed during generation. Saved work is unchanged; retry.")
    else:
        provider='owner_edited'
    row=db.scalar(select(OutreachDraft).where(OutreachDraft.lead_id == lead.id)) or OutreachDraft(lead_id=lead.id)
    row.body,row.provider=body,provider
    return save(db,row)


def report_target(db,user,kind,identifier):
    if kind=='user':
        row=get(db,User,identifier)
        if row.account_status != AccountStatus.ACTIVE or (row.profile.profile_visibility.value=='private' and row.id!=user.id):
            raise HTTPException(404,"Participant not available.")
        return {"id":row.id,"name":row.profile.display_name,"role":row.role,"account_status":row.account_status}
    if kind=='idea':
        try:
            business_ideas.view_idea(db,identifier,user)
        except (IdeaNotFound,VisibilityBlocked):
            raise HTTPException(404,"Business idea not found.")
        row=get(db,BusinessIdea,identifier)
        return {"id":row.id,"name":row.name,"owner_id":row.owner_id}
    if kind=='challenge':
        require(user,Role.BUSINESS_OWNER,Role.INNOVATOR)
        return record(challenges.visible_challenge(db,user,identifier))
    if kind=='proposal':
        row=get(db,Proposal,identifier); challenge=get(db,Challenge,row.challenge_id)
        if user.id not in (row.innovator_id,challenge.owner_id):
            raise HTTPException(404,"Record not found.")
        return record(row)
    if kind=='collaboration':
        return record(collaboration(db,user,identifier)[0])
    row=get(db,Message,identifier)
    # Reuse the exact history access policy, including verification/revocation.
    communication.authorised_thread(db,user,row.conversation_id)
    return record(row)


def log_action(db,user,action,kind,identifier,reason):
    db.add(AdminAction(actor_id=user.id,action=action,target_type=kind,target_id=identifier,reason=reason))


def moderate(db,user,payload,commit=True):
    require(user,Role.ADMIN)
    if payload.target_type=='user':
        target=get(db,User,payload.target_id,True)
        if target.role==Role.ADMIN or target.id==user.id or payload.action not in ('suspend','reactivate','deactivate'):
            raise HTTPException(422,"Administrative accounts cannot be changed here; choose a permitted participant action.")
        target.account_status={'suspend':AccountStatus.SUSPENDED,'reactivate':AccountStatus.ACTIVE,'deactivate':AccountStatus.DEACTIVATED}[payload.action]
        if target.account_status != AccountStatus.ACTIVE:
            db.execute(delete(LoginSession).where(LoginSession.user_id==target.id))
    elif payload.target_type in ('idea','challenge'):
        if payload.action not in ('hide','restore'):
            raise HTTPException(422,"Choose hide or restore for this content.")
        target=get(db,BusinessIdea if payload.target_type=='idea' else Challenge,payload.target_id,True)
        target.is_hidden=payload.action=='hide'
        if payload.target_type=='idea' and target.is_hidden:
            investment.revoke_idea_shares(db,target.id)
    else:
        if payload.action!='remove':
            raise HTTPException(422,"Only removal is supported for a reported message.")
        target=get(db,Message,payload.target_id,True)
        target.body='[Message removed by a platform administrator]'
    log_action(db,user,payload.action,payload.target_type,payload.target_id,payload.reason)
    if commit:
        db.commit()
    return {"target_id":payload.target_id,"action":payload.action}


def decide_report(db,user,identifier,payload):
    require(user,Role.ADMIN)
    row=get(db,UserReport,identifier,True)
    if row.status!='open':
        raise HTTPException(409,"This report already has a recorded decision.")
    if payload.action:
        if payload.status!='resolved' or payload.action.target_type!=row.target_type or payload.action.target_id!=row.target_id:
            raise HTTPException(422,"A report action must address its exact reported record and resolve the report.")
        moderate(db,user,payload.action,False)
    row.status,row.decision,row.reviewer_id=payload.status,payload.reason,user.id
    log_action(db,user,'report_'+payload.status,'report',row.id,payload.reason)
    return save(db,row)


def evaluation_summary(db):
    rows=list(db.scalars(select(EvaluationSession)))
    def ratio(n,d):
        count=sum(r.observations[d] for r in rows)
        return {"numerator":sum(r.observations[n] for r in rows),"denominator":count,"percent":round(100*sum(r.observations[n] for r in rows)/count,2) if count else None}
    return {"participants":len(rows),"roles":{role:sum(r.role==role for r in rows) for role in ['business_owner','innovator','investor','admin']},"browsers":sorted({r.browser for r in rows}),"tasks":ratio('tasks_without_help','tasks_attempted'),"investor_relevance":ratio('investor_relevant','investor_reviewed'),"customer_relevance":ratio('customer_relevant','customer_reviewed'),"assessment_quality":ratio('assessments_passed','assessments_reviewed'),"clarity_average":sum(r.observations['clarity'] for r in rows)/len(rows) if rows else None,"usefulness_average":sum(r.observations['usefulness'] for r in rows)/len(rows) if rows else None}
