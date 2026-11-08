"""US17-US24 endpoints; every resource is scoped on the server."""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.enums import Role, AccountStatus
from app.models.business_idea import BusinessIdea
from app.models.opportunities import Challenge, Proposal, Collaboration, Message
from app.models.completion import Lead, LeadNote, UserReport, AdminAction, EvaluationSession, Rating
from app.schemas.completion import BodyIn, RatingIn, ProfileIn, GenerateProfileIn, ImportIn, LeadIn, LeadStatusIn, ReportIn, ReportDecisionIn, AdminActionIn, EvaluationIn
from app.services import completion as service
from app.services.opportunity_access import get, owned, require, record, save

router=APIRouter(prefix='/api',tags=['Sprint 3'])
DB=Depends(get_db)
AUTH=Depends(get_current_user)

@router.get('/collaborations')
def collaborations(db:Session=DB,user:User=AUTH):
    return service.collaborations(db,user)

@router.get('/collaborations/{identifier}')
def collaboration(identifier:UUID,db:Session=DB,user:User=AUTH):
    return service.collaboration_view(db,user,identifier)

@router.post('/collaborations/{identifier}/updates',status_code=201)
def progress(identifier:UUID,payload:BodyIn,db:Session=DB,user:User=AUTH):
    return record(service.progress(db,user,identifier,payload.body))

@router.post('/collaborations/{identifier}/ready')
def ready(identifier:UUID,db:Session=DB,user:User=AUTH):
    return record(service.transition(db,user,identifier,'ready'))

@router.post('/collaborations/{identifier}/complete')
def complete(identifier:UUID,db:Session=DB,user:User=AUTH):
    return record(service.transition(db,user,identifier,'complete'))

@router.post('/collaborations/{identifier}/ratings',status_code=201)
def rate(identifier:UUID,payload:RatingIn,db:Session=DB,user:User=AUTH):
    return record(service.rate(db,user,identifier,payload))

@router.get('/profiles/{identifier}/reputation')
def reputation(identifier:UUID,db:Session=DB,user:User=AUTH):
    # Public reputation contains aggregate scores only, never private work details.
    target=get(db,User,identifier)
    if target.account_status != AccountStatus.ACTIVE or (target.profile.profile_visibility.value=='private' and target.id!=user.id):
        from fastapi import HTTPException
        raise HTTPException(404,'Profile not found.')
    count,average=db.execute(select(func.count(Rating.id),func.avg(Rating.score)).where(Rating.recipient_id==identifier)).one()
    return {'count':count,'average':float(average) if average is not None else None}

@router.get('/ideas/{identifier}/customers')
def customers(identifier:UUID,db:Session=DB,user:User=AUTH):
    row=service.profile(db,user,identifier)
    return record(row) if row else None

@router.put('/ideas/{identifier}/customers')
def edit_customers(identifier:UUID,payload:ProfileIn,db:Session=DB,user:User=AUTH):
    return record(service.write_profile(db,user,identifier,payload=payload))

@router.post('/ideas/{identifier}/customers/generate')
def generate_customers(identifier:UUID,payload:GenerateProfileIn,db:Session=DB,user:User=AUTH):
    return record(service.write_profile(db,user,identifier,kind=payload.kind))

@router.post('/ideas/{identifier}/companies/import')
def import_companies(identifier:UUID,payload:ImportIn,db:Session=DB,user:User=AUTH):
    return service.import_companies(db,user,identifier,payload)

@router.get('/ideas/{identifier}/customer-suggestions')
def suggestions(identifier:UUID,db:Session=DB,user:User=AUTH):
    return service.customer_suggestions(db,user,identifier)

@router.post('/ideas/{identifier}/leads',status_code=201)
def create_lead(identifier:UUID,payload:LeadIn,db:Session=DB,user:User=AUTH):
    return record(service.save_lead(db,user,identifier,payload))

@router.get('/leads')
def leads(db:Session=DB,user:User=AUTH):
    require(user,Role.BUSINESS_OWNER)
    return [{**record(r),'idea_name':get(db,BusinessIdea,r.idea_id).name} for r in db.scalars(select(Lead).where(Lead.owner_id==user.id).order_by(Lead.updated_at.desc()))]

@router.get('/leads/{identifier}')
def lead(identifier:UUID,db:Session=DB,user:User=AUTH):
    return service.lead_view(db,user,identifier)

@router.put('/leads/{identifier}/status')
def lead_status(identifier:UUID,payload:LeadStatusIn,db:Session=DB,user:User=AUTH):
    require(user,Role.BUSINESS_OWNER)
    row=owned(get(db,Lead,identifier,True),user);row.status=payload.status
    return record(save(db,row))

@router.post('/leads/{identifier}/notes',status_code=201)
def lead_note(identifier:UUID,payload:BodyIn,db:Session=DB,user:User=AUTH):
    require(user,Role.BUSINESS_OWNER)
    row=owned(get(db,Lead,identifier,True),user)
    return record(save(db,LeadNote(lead_id=row.id,body=payload.body)))

@router.post('/leads/{identifier}/draft')
def generate_draft(identifier:UUID,db:Session=DB,user:User=AUTH):
    return record(service.draft(db,user,identifier))

@router.put('/leads/{identifier}/draft')
def edit_draft(identifier:UUID,payload:BodyIn,db:Session=DB,user:User=AUTH):
    return record(service.draft(db,user,identifier,payload.body))

@router.post('/reports',status_code=201)
def report(payload:ReportIn,db:Session=DB,user:User=AUTH):
    service.report_target(db,user,payload.target_type,payload.target_id)
    return record(save(db,UserReport(reporter_id=user.id,**payload.model_dump())))

@router.get('/reports')
def own_reports(db:Session=DB,user:User=AUTH):
    return [record(r) for r in db.scalars(select(UserReport).where(UserReport.reporter_id==user.id).order_by(UserReport.created_at.desc()))]

@router.get('/admin/reports')
def reports(db:Session=DB,user:User=AUTH):
    require(user,Role.ADMIN)
    return [record(r) for r in db.scalars(select(UserReport).order_by(UserReport.created_at.desc()))]

@router.get('/admin/reports/{identifier}')
def inspect_report(identifier:UUID,db:Session=DB,user:User=AUTH):
    require(user,Role.ADMIN);row=get(db,UserReport,identifier)
    model={'user':User,'idea':BusinessIdea,'challenge':Challenge,'proposal':Proposal,'collaboration':Collaboration,'message':Message}[row.target_type]
    target=db.get(model,row.target_id)
    if target is None: context={'unavailable':True}
    elif row.target_type=='user':context={'id':target.id,'name':target.profile.display_name,'role':target.role,'account_status':target.account_status}
    elif row.target_type=='idea':context={'id':target.id,'name':target.name,'problem':target.problem,'solution':target.solution,'is_hidden':target.is_hidden}
    else:context=record(target)
    service.log_action(db,user,'inspect_report','report',row.id,'Inspected the reported record for moderation');db.commit()
    return {**record(row),'reported_record':context}

@router.post('/admin/reports/{identifier}/decision')
def decide_report(identifier:UUID,payload:ReportDecisionIn,db:Session=DB,user:User=AUTH):
    return record(service.decide_report(db,user,identifier,payload))

@router.post('/admin/actions')
def moderate(payload:AdminActionIn,db:Session=DB,user:User=AUTH):
    return service.moderate(db,user,payload)

@router.get('/admin/activity')
def activity(db:Session=DB,user:User=AUTH):
    require(user,Role.ADMIN)
    return {'counts':{name:db.scalar(select(func.count()).select_from(model)) for name,model in [('accounts',User),('challenges',Challenge),('proposals',Proposal),('collaborations',Collaboration),('reports',UserReport)]},'actions':[record(r) for r in db.scalars(select(AdminAction).order_by(AdminAction.created_at.desc()).limit(100))]}

@router.get('/admin/accounts')
def accounts(db:Session=DB,user:User=AUTH):
    require(user,Role.ADMIN)
    return [{'id':r.id,'name':r.profile.display_name,'role':r.role,'status':r.account_status} for r in db.scalars(select(User).order_by(User.created_at.desc()).limit(300))]

@router.get('/admin/evaluation')
def evaluation(db:Session=DB,user:User=AUTH):
    require(user,Role.ADMIN)
    return service.evaluation_summary(db)

@router.post('/admin/evaluation',status_code=201)
def record_evaluation(payload:EvaluationIn,db:Session=DB,user:User=AUTH):
    require(user,Role.ADMIN)
    values=payload.model_dump();values.pop('consent_confirmed')
    row=EvaluationSession(participant_code=values.pop('participant_code'),role=values.pop('role'),browser=values.pop('browser'),observations=values)
    db.add(row);db.flush();service.log_action(db,user,'record_evaluation','evaluation',row.id,'Recorded consent-confirmed anonymised observations')
    return record(save(db,row))
