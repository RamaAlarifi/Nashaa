"""Explicit, idempotent fictional Sprint 3 demonstration records. Never evaluation data."""
from sqlalchemy import select
from app.config import get_settings
from app.database import SessionLocal
from app.models.user import User
from app.models.enums import Role
from app.models.business_idea import BusinessIdea
from app.models.opportunities import Challenge, Proposal, Collaboration
from app.models.completion import CustomerProfile, LeadSource, CompanyRecord
from app.services.auth import create_user
from app.services.completion import parse_companies
from app.schemas.completion import ImportIn

def main():
    if get_settings().environment != 'development':
        raise RuntimeError('Fictional demonstration seeding is restricted to development.')
    with SessionLocal() as db:
        users={}
        for label,role in [('owner',Role.BUSINESS_OWNER),('innovator',Role.INNOVATOR),('investor',Role.INVESTOR),('admin',Role.ADMIN)]:
            email=f's3-{label}@example.com'
            row=db.scalar(select(User).where(User.email==email))
            if not row:
                row=create_user(db,email=email,password='Password123!',role=role,display_name=f'Fictional Sprint 3 {label}')
                row.verification_status='approved';db.commit()
            users[label]=row
        idea=db.scalar(select(BusinessIdea).where(BusinessIdea.owner_id==users['owner'].id,BusinessIdea.name=='Fictional Sprint 3 Cup Pilot'))
        if not idea:
            idea=BusinessIdea(owner_id=users['owner'].id,name='Fictional Sprint 3 Cup Pilot',problem='Campus cafes need to reduce disposable cup waste.',solution='A small returnable-cup supply and washing pilot.',industry='manufacturing_packaging',intended_customers='Campus cafes',target_location='Riyadh')
            db.add(idea);db.flush()
            db.add(CustomerProfile(idea_id=idea.id,kind='business',idea_revision=1,provider='owner_edited',details={'customer_type':'Small campus cafes','industry':'manufacturing_packaging','location':'Riyadh','size':'Small business','main_need':'Reduce disposable cup waste','buying_motivation':'Test reuse operations','objections':'Washing costs and loss rates unknown','channels':'Permission-based cafe interviews','assumptions':'Fictional demonstration hypothesis; demand is unvalidated.'}))
            source=LeadSource(owner_id=users['owner'].id,idea_id=idea.id,name='Fictional Sprint 3 demonstration companies created for local testing',filename='fictional-s3.csv',permission='Fictional data created for the demonstration',fictional=True);db.add(source);db.flush()
            parsed=parse_companies(ImportIn(filename='fictional.csv',source=source.name,permission_confirmed=True,fictional=True,csv_text='company_name,industry,location,website,business_need\nFictional Campus Cafe,manufacturing_packaging,Riyadh,https://example.com,Reduce disposable cup waste\n'))
            for item in parsed:db.add(CompanyRecord(idea_id=idea.id,source_id=source.id,name=item.pop('company_name'),**item))
            challenge=Challenge(owner_id=users['owner'].id,idea_id=idea.id,title='Fictional Sprint 3 cup return prototype',problem=idea.problem,desired_outcome='A tested return station prototype',industry=idea.industry,required_skills=['Design'],timeline='4 weeks',status='closed');db.add(challenge);db.flush()
            proposal=Proposal(challenge_id=challenge.id,innovator_id=users['innovator'].id,approach='Build and test a simple cup return station.',deliverables='Prototype design and test notes.',timeline='4 weeks',status='selected');db.add(proposal);db.flush()
            db.add(Collaboration(challenge_id=challenge.id,selected_proposal_id=proposal.id))
            db.commit()
    print('Fictional Sprint 3 accounts, customer example and active collaboration are ready. No evaluation results were seeded.')

if __name__=='__main__':main()
