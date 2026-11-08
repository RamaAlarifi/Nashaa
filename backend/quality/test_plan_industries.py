"""Industry validation/discovery and Gemini request/failure regressions."""
import json
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import httpx
import pytest
from fastapi import HTTPException

from app.ai.base import AIConfigurationError, AIQuotaError, AIResponseError, AIServiceError, AITimeoutError, AssessmentInput
from app.ai.gemini import GeminiAssessmentProvider, SOURCE_DISCLOSURE, SYSTEM_INSTRUCTION, _build_prompt
from app.industries import canonical, industry_key, validate_industry
from app.models.enums import AccountStatus, ProfileVisibility
from app.models.user import User
from quality.conftest import auth_headers, register_and_login

PLANS = json.loads((Path(__file__).parent / "fixtures/business_plans.json").read_text())


@pytest.mark.parametrize("value,expected", [("Packaging","manufacturing_packaging"),("Sustainable packaging","manufacturing_packaging"),("Health tech","healthcare"),(" Tech ","software_it"),("software_it","software_it"),("","")])
def test_industry_normalisation(value, expected):
    assert validate_industry(value) == expected


def test_unknown_legacy_is_preserved_but_not_accepted_as_new():
    assert validate_industry("Legacy niche", "Legacy niche") == "Legacy niche"
    with pytest.raises(HTTPException): validate_industry("Legacy niche")
    with pytest.raises(HTTPException): validate_industry("", required=True)
    assert industry_key("Legacy niche") != industry_key("other")


def test_catalogue_profiles_and_missing_industry(client):
    catalogue=client.get("/api/industries").json()
    assert len(catalogue)==len({c['id'] for c in catalogue}) and any(c['id']=='software_it' for c in catalogue)
    _,token=register_and_login(client); headers=auth_headers(token)
    assert client.put('/api/profile',headers=headers,json={'role_specific_info':{'business_name':'Empty industry','industry':''}}).status_code==200
    assert client.put('/api/profile',headers=headers,json={'role_specific_info':{'industry':'Arbitrary new category'}}).status_code==422
    saved=client.put('/api/profile',headers=headers,json={'role_specific_info':{'industry':'Packaging','industry_detail':'Restaurant containers'}})
    assert saved.json()['role_specific_info']['industry']=='manufacturing_packaging'
    assert client.get('/api/profile',headers=headers).json()['role_specific_info']['industry_detail']=='Restaurant containers'


def test_unknown_legacy_profile_can_be_saved_without_changing_its_industry(client,db):
    account,token=register_and_login(client)
    user=db.get(User,UUID(account['user']['id']))
    user.profile.role_specific_info={'business_name':'Old business','industry':'Legacy niche not in catalogue'}
    db.commit()
    response=client.put('/api/profile',headers=auth_headers(token),json={'display_name':'Updated owner','role_specific_info':{'business_name':'Updated business','industry':'Legacy niche not in catalogue'}})
    assert response.status_code==200
    assert response.json()['role_specific_info']['industry']=='Legacy niche not in catalogue'


def test_profile_discovery_visibility_roles_and_industries(client,db):
    owner,ot=register_and_login(client,email='directory-owner@example.com',display_name='Visible Packaging Owner')
    _,it=register_and_login(client,email='directory-investor@example.com',role='investor',display_name='Visible Packaging Investor')
    _,vt=register_and_login(client,email='directory-viewer@example.com',role='innovator')
    oh,ih,vh=auth_headers(ot),auth_headers(it),auth_headers(vt)
    client.put('/api/profile',headers=oh,json={'role_specific_info':{'industry':'Packaging'}})
    client.put('/api/investor-preferences',headers=ih,json={'industries':['Sustainable packaging'],'stages':['idea'],'min_funding':'0','max_funding':'100000','locations':[]})
    rows=client.get('/api/profiles?industry=manufacturing_packaging',headers=vh).json()
    assert {r['role'] for r in rows}=={'business_owner','investor'}
    assert all('email' not in r and 'role_specific_info' not in r for r in rows)
    assert len(client.get('/api/profiles?industry=manufacturing_packaging&role=business_owner',headers=vh).json())==1
    assert client.get('/api/profiles?industry=education',headers=vh).json()==[]
    assert client.get('/api/profiles?industry=invalid-category',headers=vh).status_code==422
    client.put('/api/profile',headers=oh,json={'profile_visibility':'private'})
    assert len(client.get('/api/profiles?industry=manufacturing_packaging',headers=vh).json())==1
    user=db.get(User,UUID(owner['user']['id']));user.account_status=AccountStatus.SUSPENDED;db.commit()
    assert client.get(f"/api/users/{user.id}/profile",headers=vh).status_code==404
    assert client.get('/api/profiles').status_code==401


def test_plan_fields_saved_revision_snapshot_and_summary_privacy(client):
    _,token=register_and_login(client); headers=auth_headers(token)
    response=client.post('/api/ideas',headers=headers,json={**PLANS[0],'visibility':'registered'})
    assert response.status_code==201,response.text
    idea=response.json(); assert idea['industry']=='manufacturing_packaging'
    changed=client.put(f"/api/ideas/{idea['id']}",headers=headers,json={'revenue_model':'Revised rental price pending validation.'}).json()
    assert changed['revision_number']==2
    status=client.post(f"/api/ideas/{idea['id']}/assessment",headers=headers).json()
    assert status['latest_valid']['input_snapshot']['revenue_model']==changed['revenue_model']
    _,other=register_and_login(client,email='summary-viewer@example.com',role='investor')
    summary=client.get(f"/api/ideas/{idea['id']}",headers=auth_headers(other)).json()
    for key in ('revenue_model','cost_structure','competition','business_model','growth_strategy','industry_detail'):
        assert key not in summary
    assert client.post('/api/ideas',headers=headers,json={'name':'Bad industry','industry':'made-up-category'}).status_code==422


def test_two_plans_reach_distinct_prompts_without_inventing_missing_fields():
    first,second=[_build_prompt(AssessmentInput(**p)) for p in PLANS]
    assert first!=second and 'reusable' in first and 'receptionists' in second
    assert PLANS[0]['revenue_model'] in first
    assert 'never invent' in SYSTEM_INSTRUCTION.lower()
    sparse=AssessmentInput(**{**PLANS[0],'revenue_model':'','competition':''})
    assert '"revenue_model": ""' in _build_prompt(sparse)


def mock_provider(monkeypatch, handler):
    real_client=httpx.Client
    monkeypatch.setattr('app.ai.gemini.httpx.Client',lambda **kwargs: real_client(transport=httpx.MockTransport(handler),**kwargs))
    return GeminiAssessmentProvider(api_key='fictional-key',model='gemini-test',timeout=1)


def test_gemini_uses_schema_system_instruction_and_truthful_sources(monkeypatch):
    def handler(request):
        assert request.headers['x-goog-api-key']=='fictional-key'
        payload=json.loads(request.content)
        assert payload['generationConfig']['responseFormat']['text']['mimeType']=='APPLICATION_JSON'
        assert payload['systemInstruction']['parts'][0]['text']==SYSTEM_INSTRUCTION
        assert 'professional tone that feels human-written' in SYSTEM_INSTRUCTION
        assert 'must never weaken' in SYSTEM_INSTRUCTION
        assert 'Never invent market sizes' in SYSTEM_INSTRUCTION
        assert PLANS[1]['growth_strategy'] in payload['contents'][0]['parts'][0]['text']
        content={key:'Specific fictional clinic assessment.' for key in ['market_considerations','target_customer_analysis','competitor_considerations','indicative_costs','suggested_next_steps','assumptions']}
        content['sources']='Invented research claim must not be retained.'
        return httpx.Response(200,json={'candidates':[{'finishReason':'STOP','content':{'parts':[{'thought':True,'text':'Hidden thinking'}, {'text':json.dumps(content)}]}}]})
    result=mock_provider(monkeypatch,handler).generate(AssessmentInput(**PLANS[1]))
    assert result.sources==SOURCE_DISCLOSURE and 'Hidden thinking' not in result.model_dump_json()


@pytest.mark.parametrize('code',[400,401,403,404,429,500])
def test_gemini_http_failure_never_substitutes_mock(monkeypatch,code):
    provider=mock_provider(monkeypatch,lambda _:httpx.Response(code,json={'error':{'message':'private diagnostic'}}))
    with pytest.raises(AIServiceError) as error: provider.generate(AssessmentInput(**PLANS[0]))
    assert 'private diagnostic' not in str(error.value)
    if code==429: assert isinstance(error.value,AIQuotaError)


@pytest.mark.parametrize('payload',[
    [],{}, {'candidates':[]}, {'candidates':[{'finishReason':'MAX_TOKENS','content':{'parts':[{'text':'{}'}]}}]},
    {'candidates':[{'finishReason':'SAFETY'}]}, {'candidates':[{'content':{'parts':[{'text':'not json'}]}}]},
    {'candidates':[{'content':{'parts':[{'text':'{}'}]}}]},
])
def test_gemini_invalid_or_incomplete_output(monkeypatch,payload):
    provider=mock_provider(monkeypatch,lambda _:httpx.Response(200,json=payload))
    with pytest.raises(AIResponseError): provider.generate(AssessmentInput(**PLANS[0]))


def test_gemini_timeout(monkeypatch):
    def timeout(request): raise httpx.ReadTimeout('fictional timeout',request=request)
    with pytest.raises(AITimeoutError): mock_provider(monkeypatch,timeout).generate(AssessmentInput(**PLANS[0]))


def test_missing_key_does_not_fall_back_to_simulation(monkeypatch):
    from app.ai import factory
    monkeypatch.setattr(factory,'_cached',None)
    monkeypatch.setattr(factory,'get_settings',lambda:SimpleNamespace(ai_provider='gemini',gemini_api_key=''))
    # Constructor reads regular settings separately; supply an empty-key setting there too.
    monkeypatch.setattr('app.ai.gemini.get_settings',lambda:SimpleNamespace(gemini_api_key='',gemini_model='gemini-test',ai_timeout_seconds=1))
    with pytest.raises(AIConfigurationError): factory.get_assessment_provider()


def test_quota_failure_preserves_previous_result(client,with_ai_provider):
    from app.ai.mock import MockAssessmentProvider
    _,token=register_and_login(client);headers=auth_headers(token)
    idea=client.post('/api/ideas',headers=headers,json=PLANS[0]).json()
    path=f"/api/ideas/{idea['id']}/assessment"
    previous=client.post(path,headers=headers).json()['latest_valid']['id']
    class NoQuota(MockAssessmentProvider):
        def generate(self,data): raise AIQuotaError('private provider diagnostic')
    with_ai_provider(NoQuota())
    failed=client.post(path,headers=headers).json()
    assert failed['current_status']=='failed' and failed['latest_valid']['id']==previous
    assert 'quota' in failed['error_message'] and 'private provider diagnostic' not in failed['error_message']


@pytest.mark.parametrize("code", [502, 503, 504])
def test_gemini_temporary_outage_is_classified(monkeypatch, code):
    from app.ai.base import AIUnavailableError
    provider = mock_provider(monkeypatch, lambda _: httpx.Response(code, json={"error": {"message": "private diagnostic"}}))
    with pytest.raises(AIUnavailableError) as error:
        provider.generate(AssessmentInput(**PLANS[0]))
    assert "private diagnostic" not in str(error.value)


def test_outage_failure_preserves_previous_result(client, with_ai_provider):
    from app.ai.base import AIUnavailableError
    from app.ai.mock import MockAssessmentProvider
    _, token = register_and_login(client)
    headers = auth_headers(token)
    idea = client.post("/api/ideas", headers=headers, json=PLANS[0]).json()
    path = f"/api/ideas/{idea['id']}/assessment"
    previous = client.post(path, headers=headers).json()["latest_valid"]["id"]

    class Unavailable(MockAssessmentProvider):
        def generate(self, data):
            raise AIUnavailableError("private provider diagnostic")

    with_ai_provider(Unavailable())
    failed = client.post(path, headers=headers).json()
    assert failed["current_status"] == "failed"
    assert failed["latest_valid"]["id"] == previous
    assert "temporarily unavailable" in failed["error_message"]
    assert "private provider diagnostic" not in failed["error_message"]


def test_timeout_failure_preserves_previous_result(client, with_ai_provider):
    from app.ai.mock import MockAssessmentProvider
    _, token = register_and_login(client)
    headers = auth_headers(token)
    idea = client.post("/api/ideas", headers=headers, json=PLANS[0]).json()
    path = f"/api/ideas/{idea['id']}/assessment"
    previous = client.post(path, headers=headers).json()["latest_valid"]["id"]
    class TimedOut(MockAssessmentProvider):
        def generate(self, data):
            raise AITimeoutError("private diagnostic")
    with_ai_provider(TimedOut())
    failed = client.post(path, headers=headers).json()
    assert failed["current_status"] == "failed"
    assert failed["latest_valid"]["id"] == previous
    assert "took too long" in failed["error_message"]
    assert "private diagnostic" not in failed["error_message"]
