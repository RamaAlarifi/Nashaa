"""Real-provider transport contract without live API use or real credentials."""
import json
from types import SimpleNamespace
import httpx
import pytest
from app.ai.discovery import generate_fields
from app.ai.base import AIServiceError

def setup(monkeypatch,handler):
    real=httpx.Client
    monkeypatch.setattr('app.ai.discovery.get_settings',lambda:SimpleNamespace(ai_provider='gemini'))
    monkeypatch.setattr('app.ai.discovery.GeminiAssessmentProvider',lambda:SimpleNamespace(_timeout=1,_api_key='fictional-key',_model='fictional-model'))
    monkeypatch.setattr('app.ai.discovery.httpx.Client',lambda **kw:real(transport=httpx.MockTransport(handler),**kw))

def test_discovery_context_and_schema_are_sent_only_to_server_provider(monkeypatch):
    def handler(request):
        assert request.headers['x-goog-api-key']=='fictional-key'
        payload=json.loads(request.content)
        assert 'Never invent customers' in payload['systemInstruction']['parts'][0]['text']
        assert 'Fictional cafe' in payload['contents'][0]['parts'][0]['text']
        return httpx.Response(200,json={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps({'body':'Specific draft for the fictional cafe.'})}]}}]})
    setup(monkeypatch,handler)
    result,provider=generate_fields('Draft only.',{'name':'Fictional cafe'},['body'],{})
    assert provider=='gemini' and 'fictional cafe' in result['body']

@pytest.mark.parametrize('code',[400,401,429,503])
def test_discovery_http_errors_do_not_return_simulation_or_provider_secrets(monkeypatch,code):
    setup(monkeypatch,lambda _:httpx.Response(code,json={'error':{'message':'private diagnostic'}}))
    with pytest.raises(AIServiceError) as error:generate_fields('Draft',{},['body'],{'body':'mock content'})
    assert 'private diagnostic' not in str(error.value)

@pytest.mark.parametrize('response',[{},[],{'candidates':[{'finishReason':'MAX_TOKENS'}]},{'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':'invalid JSON'}]}}]},{'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':'{"body": ""}'}]}}]}])
def test_discovery_invalid_output_is_rejected(monkeypatch,response):
    setup(monkeypatch,lambda _:httpx.Response(200,json=response))
    with pytest.raises(AIServiceError):generate_fields('Draft',{},['body'],{})

def test_discovery_timeout_is_clear(monkeypatch):
    def timeout(request):raise httpx.ReadTimeout('provider timeout',request=request)
    setup(monkeypatch,timeout)
    with pytest.raises(AIServiceError,match='timed out'):generate_fields('Draft',{},['body'],{})
