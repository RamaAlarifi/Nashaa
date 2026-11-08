"""Charter US17-US24: executed acceptance, privacy and failure regressions."""
from uuid import uuid4
import pytest
from pydantic import ValidationError
from app.ai.base import AIServiceError
from app.models.completion import CustomerProfile, Lead, LeadSource, AdminAction
from app.models.user import User
from app.models.enums import AccountStatus
from app.schemas.completion import BodyIn, RatingIn, ImportIn, EvaluationIn
from app.services.completion import parse_companies
from quality.test_sprint2 import actors, approved, challenge, PROPOSAL
from quality.conftest import register_and_login, auth_headers

DETAILS=dict(customer_type='Independent campus cafes',industry='manufacturing_packaging',location='Riyadh',size='Small businesses',main_need='Reusable packaging waste reduction',buying_motivation='Reduce cup waste',objections='Washing costs unknown',channels='Permission-based cafe interviews',assumptions='Demand is not validated')
CSV='company_name,industry,location,website,business_need\nFictional Campus Cafe,manufacturing_packaging,Riyadh,https://example.com,Reusable packaging waste\n'

@pytest.fixture
def idea(client,actors):
    r=client.post('/api/ideas',headers=actors['owner']['headers'],json=dict(name='Fictional S3 cup pilot',problem='Reusable packaging waste',solution='Returnable cups for cafes',industry='manufacturing_packaging',intended_customers='Campus cafes',target_location='Riyadh',visibility='registered'))
    assert r.status_code==201,r.text
    return r.json()

def customer_setup(client,actors,idea):
    h=actors['owner']['headers'];path=f"/api/ideas/{idea['id']}"
    r=client.put(path+'/customers',headers=h,json={'kind':'business','details':DETAILS});assert r.status_code==200,r.text
    r=client.post(path+'/companies/import',headers=h,json={'filename':'fictional.csv','source':'Fictional documentation records; created for tests','permission_confirmed':True,'fictional':True,'csv_text':CSV});assert r.status_code==200,r.text
    suggestions=client.get(path+'/customer-suggestions',headers=h).json();assert suggestions['items']
    lead=client.post(path+'/leads',headers=h,json={'kind':'customer','reference_id':suggestions['items'][0]['id']});assert lead.status_code==201,lead.text
    return path,lead.json(),suggestions

def work_setup(client,actors):
    approved(client,actors,'innovator');c=challenge(client,actors)
    p=client.post(f"/api/challenges/{c['id']}/proposals",headers=actors['innovator']['headers'],json=PROPOSAL).json()
    r=client.post(f"/api/challenges/{c['id']}/select/{p['id']}",headers=actors['owner']['headers']);assert r.status_code==201,r.text
    return '/api/collaborations/'+r.json()['id'],c

def test_us17_us22_complete_journey_and_privacy(client,actors):
    path,c=work_setup(client,actors);oh=actors['owner']['headers'];ih=actors['innovator']['headers']
    assert len(client.get('/api/collaborations',headers=oh).json())==1
    assert client.post(path+'/ratings',headers=oh,json={'score':5}).status_code==409
    assert client.post(path+'/complete',headers=oh).status_code==409
    assert client.post(path+'/ready',headers=oh).status_code==403
    for h in [oh,ih]:assert client.post(path+'/updates',headers=h,json={'body':'A meaningful prototype progress update.'}).status_code==201
    assert len(client.get(path,headers=ih).json()['updates'])==2
    _,token=register_and_login(client,email='outsider-s3@example.com',role='innovator')
    for suffix in ['', '/updates','/ready','/ratings']:
        r=client.get(path,headers=auth_headers(token)) if not suffix else client.post(path+suffix,headers=auth_headers(token),json={'body':'Outsider update'} if suffix=='/updates' else {'score':4} if suffix=='/ratings' else None)
        assert r.status_code==404,r.text
    assert client.post(path+'/ready',headers=ih).json()['status']=='ready'
    assert client.post(path+'/complete',headers=ih).status_code==403
    assert client.post(path+'/complete',headers=oh).json()['status']=='completed'
    assert client.post(path+'/complete',headers=oh).status_code==409
    assert client.post(path+'/updates',headers=oh,json={'body':'Too late'}).status_code==409
    for h in [oh,ih]:assert client.post(path+'/ratings',headers=h,json={'score':4,'comment':'Clear agreed deliverables.'}).status_code==201
    assert client.post(path+'/ratings',headers=oh,json={'score':5}).status_code==409
    assert client.get(f"/api/profiles/{actors['innovator']['id']}/reputation",headers=oh).json()['average']==4

def test_us18_generate_refine_private_saved_profile(client,actors,idea):
    path=f"/api/ideas/{idea['id']}/customers";h=actors['owner']['headers']
    r=client.post(path+'/generate',headers=h,json={'kind':'business'});assert r.status_code==200,r.text
    assert 'Reusable packaging' in r.json()['details']['main_need']
    r=client.put(path,headers=h,json={'kind':'business','details':DETAILS});assert r.status_code==200,r.text
    assert client.get(path,headers=h).json()['details']==DETAILS
    assert client.get(path,headers=actors['investor']['headers']).status_code==403
    other,token=register_and_login(client,email='other-owner-s3@example.com');assert client.get(path,headers=auth_headers(token)).status_code==404

def test_us18_generation_failure_preserves_profile(client,actors,idea,monkeypatch):
    h=actors['owner']['headers'];path=f"/api/ideas/{idea['id']}/customers"
    client.put(path,headers=h,json={'kind':'business','details':DETAILS})
    def failed(*a,**k):raise AIServiceError('private provider details')
    monkeypatch.setattr('app.services.completion.generate_fields',failed)
    r=client.post(path+'/generate',headers=h,json={'kind':'business'});assert r.status_code==503
    assert 'private provider details' not in r.text
    assert client.get(path,headers=h).json()['details']==DETAILS

def test_us19_us21_source_duplicates_saved_followup(client,actors,idea):
    path,lead,suggestions=customer_setup(client,actors,idea);h=actors['owner']['headers'];lp='/api/leads/'+lead['id']
    assert suggestions['items'][0]['score']==100
    assert suggestions['items'][0]['fictional'] is True
    repeated=client.post(path+'/leads',headers=h,json={'kind':'customer','reference_id':suggestions['items'][0]['id']});assert repeated.json()['id']==lead['id']
    repeated=client.post(path+'/companies/import',headers=h,json={'filename':'again.csv','source':'Permission-confirmed repeated records','permission_confirmed':True,'csv_text':CSV});assert repeated.json()['duplicates_skipped']==1
    assert client.put(lp+'/status',headers=h,json={'status':'follow_up_needed'}).status_code==200
    assert client.post(lp+'/notes',headers=h,json={'body':'Discuss washing cost assumptions next week.'}).status_code==201
    reopened=client.get(lp,headers=h).json();assert reopened['status']=='follow_up_needed' and len(reopened['notes'])==1
    assert reopened['snapshot']['source']=='Fictional documentation records; created for tests'
    assert client.get(lp,headers=actors['investor']['headers']).status_code==403
    _,token=register_and_login(client,email='lead-outsider@example.com')
    for suffix in ['', '/notes','/status','/draft']:
        r=client.get(lp,headers=auth_headers(token)) if not suffix else client.post(lp+suffix,headers=auth_headers(token),json={'body':'Private note'}) if suffix=='/notes' else client.put(lp+suffix,headers=auth_headers(token),json={'status':'closed'}) if suffix=='/status' else client.post(lp+suffix,headers=auth_headers(token))
        assert r.status_code==404,r.text

def test_us19_consumer_gets_segments_not_company_contacts(client,actors,idea):
    h=actors['owner']['headers'];path=f"/api/ideas/{idea['id']}"
    client.put(path+'/customers',headers=h,json={'kind':'consumer','details':{**DETAILS,'customer_type':'Students using campus cafes'}})
    r=client.get(path+'/customer-suggestions',headers=h).json();assert r['items']==[] and r['segments']==['Students using campus cafes'] and r['channels']==DETAILS['channels']
    assert client.post(path+'/companies/import',headers=h,json={'filename':'x.csv','source':'Permitted fictional dataset','permission_confirmed':True,'csv_text':CSV}).status_code==409

def test_us19_invalid_file_is_atomic(client,actors,idea,db):
    h=actors['owner']['headers'];path=f"/api/ideas/{idea['id']}"
    client.put(path+'/customers',headers=h,json={'kind':'business','details':DETAILS})
    r=client.post(path+'/companies/import',headers=h,json={'filename':'x.csv','source':'Fictional dataset with invalid second row','permission_confirmed':True,'csv_text':CSV+'Broken row\n'});assert r.status_code==422
    from sqlalchemy import select,func
    assert db.scalar(select(func.count()).select_from(LeadSource))==0

def test_us20_draft_context_edit_failure_preserves_work(client,actors,idea,monkeypatch):
    _,lead,_=customer_setup(client,actors,idea);h=actors['owner']['headers'];path='/api/leads/'+lead['id']
    r=client.post(path+'/draft',headers=h);assert r.status_code==200,r.text
    assert 'Fictional Campus Cafe' in r.json()['body'] and idea['name'] in r.json()['body']
    assert client.put(path+'/draft',headers=h,json={'body':'An owner-reviewed draft for this cafe.'}).status_code==200
    def failed(*a,**k):raise AIServiceError('provider unavailable')
    monkeypatch.setattr('app.services.completion.generate_fields',failed)
    assert client.post(path+'/draft',headers=h).status_code==503
    saved=client.get(path,headers=h).json();assert saved['draft']['body']=='An owner-reviewed draft for this cafe.' and saved['snapshot']['name']=='Fictional Campus Cafe'

def test_us21_investor_lead_saved(client,actors,idea):
    h=actors['owner']['headers']
    client.put('/api/investor-preferences',headers=actors['investor']['headers'],json={'industries':['manufacturing_packaging'],'stages':['idea'],'locations':[],'min_funding':'0','max_funding':'100000'})
    r=client.post(f"/api/ideas/{idea['id']}/leads",headers=h,json={'kind':'investor','reference_id':actors['investor']['id']});assert r.status_code==201,r.text
    assert r.json()['snapshot']['name']=='Fictional investor'

def test_us23_us24_report_review_moderation_and_audit(client,actors,idea):
    oh=actors['owner']['headers'];ah=actors['admin']['headers'];ih=actors['investor']['headers']
    report=client.post('/api/reports',headers=oh,json={'target_type':'idea','target_id':idea['id'],'category':'inappropriate_content','description':'Fictional reported content requiring moderation review.'});assert report.status_code==201,report.text
    rp='/api/admin/reports/'+report.json()['id']
    assert client.get('/api/admin/reports',headers=ih).status_code==403
    assert client.get(rp,headers=ah).json()['reported_record']['name']==idea['name']
    assert client.post(rp+'/decision',headers=ah,json={'status':'resolved','reason':'Tested moderation action recorded.','action':{'target_type':'idea','target_id':str(uuid4()),'action':'hide','reason':'Incorrect target must not change anything.'}}).status_code==422
    r=client.post(rp+'/decision',headers=ah,json={'status':'resolved','reason':'Reported content is hidden pending correction.','action':{'target_type':'idea','target_id':idea['id'],'action':'hide','reason':'Reported content is hidden pending correction.'}});assert r.status_code==200,r.text
    assert client.get(f"/api/ideas/{idea['id']}",headers=ih).status_code==404
    # An ordinary owner edit/visibility update must not undo moderation.
    client.patch(f"/api/ideas/{idea['id']}/visibility",headers=oh,json={'visibility':'registered'})
    assert client.get(f"/api/ideas/{idea['id']}",headers=ih).status_code==404
    actions=client.get('/api/admin/activity',headers=ah).json()['actions'];assert {'hide','report_resolved','inspect_report'}<={a['action'] for a in actions}
    assert client.get('/api/reports',headers=oh).json()[0]['status']=='resolved'
    assert client.post(rp+'/decision',headers=ah,json={'status':'dismissed','reason':'Duplicate decision'}).status_code==409

def test_admin_account_actions_revoke_sessions_and_protect_admin(client,actors):
    ah=actors['admin']['headers'];payload={'target_type':'user','target_id':actors['investor']['id'],'action':'suspend','reason':'Fictional suspension for access-control testing.'}
    assert client.post('/api/admin/actions',headers=ah,json=payload).status_code==200
    assert client.get('/api/dashboard',headers=actors['investor']['headers']).status_code==401
    assert client.post('/api/admin/actions',headers=ah,json={**payload,'action':'reactivate'}).status_code==200
    assert client.get('/api/dashboard',headers=actors['investor']['headers']).status_code==401
    assert client.post('/api/admin/actions',headers=ah,json={**payload,'target_id':actors['admin']['id']}).status_code==422

def test_private_message_and_unknown_target_report_rejected(client,actors):
    r=client.post('/api/reports',headers=actors['owner']['headers'],json={'target_type':'message','target_id':str(uuid4()),'category':'privacy','description':'Invalid record cannot be reported.'});assert r.status_code==404

def test_private_idea_cannot_be_reported_by_an_outsider(client,actors,idea):
    h=actors['owner']['headers']
    client.patch(f"/api/ideas/{idea['id']}/visibility",headers=h,json={'visibility':'private'})
    response=client.post('/api/reports',headers=actors['investor']['headers'],json={'target_type':'idea','target_id':idea['id'],'category':'privacy','description':'An outsider cannot inspect or report private idea content.'})
    assert response.status_code==404

def test_profile_generation_cannot_overwrite_intervening_owner_edit(client,actors,idea,db,monkeypatch):
    from sqlalchemy import select
    path=f"/api/ideas/{idea['id']}/customers";h=actors['owner']['headers']
    client.put(path,headers=h,json={'kind':'business','details':DETAILS})
    def edited(*args,**kwargs):
        row=db.scalar(select(CustomerProfile).where(CustomerProfile.idea_id==idea['id']))
        row.details={**row.details,'customer_type':'Owner revised the target while generation was pending'};db.commit()
        return DETAILS,'mock'
    monkeypatch.setattr('app.services.completion.generate_fields',edited)
    assert client.post(path+'/generate',headers=h,json={'kind':'business'}).status_code==409
    assert client.get(path,headers=h).json()['details']['customer_type'].startswith('Owner revised')

def test_evaluation_empty_and_actual_observation_counts(client,actors):
    ah=actors['admin']['headers'];empty=client.get('/api/admin/evaluation',headers=ah).json();assert empty['participants']==0 and empty['tasks']['percent'] is None
    sample={'participant_code':'TEST-P01','role':'business_owner','browser':'Controlled test browser','consent_confirmed':True,'tasks_attempted':5,'tasks_without_help':4,'customer_reviewed':5,'customer_relevant':4,'clarity':4,'usefulness':5}
    assert client.post('/api/admin/evaluation',headers=actors['owner']['headers'],json=sample).status_code==403
    assert client.post('/api/admin/evaluation',headers=ah,json=sample).status_code==201
    result=client.get('/api/admin/evaluation',headers=ah).json();assert result['tasks']['percent']==80 and result['customer_relevance']['percent']==80 and result['investor_relevance']['percent'] is None
    assert client.post('/api/admin/evaluation',headers=ah,json={**sample,'participant_code':'TEST-P02','tasks_without_help':6}).status_code==422

@pytest.mark.parametrize('csv_text',[CSV.replace('company_name','email'),CSV+'=IMPORTXML(x),manufacturing_packaging,Riyadh,,waste\n',CSV.replace('https://example.com','javascript:alert(1)'),CSV.replace('https://example.com','https://user:password@example.com'),CSV+'Bad,record\n',CSV.splitlines()[0]+'\n',CSV+('\n'.join('Cafe'+str(i)+',manufacturing_packaging,Riyadh,,waste' for i in range(201)))])
def test_import_validation_boundaries(csv_text):
    from fastapi import HTTPException
    with pytest.raises(HTTPException):parse_companies(ImportIn(filename='test.csv',source='Permission-confirmed test source',permission_confirmed=True,csv_text=csv_text))

@pytest.mark.parametrize('model,payload',[(BodyIn,{'body':' '}),(RatingIn,{'score':0}),(RatingIn,{'score':6}),(RatingIn,{'score':4,'author_id':str(uuid4())}),(ImportIn,{'filename':'../bad.csv','source':'Test source','permission_confirmed':True,'csv_text':CSV}),(ImportIn,{'filename':'test.csv','source':'Test source','permission_confirmed':False,'csv_text':CSV})])
def test_command_boundaries_and_spoofing(model,payload):
    with pytest.raises(ValidationError):model.model_validate(payload)
