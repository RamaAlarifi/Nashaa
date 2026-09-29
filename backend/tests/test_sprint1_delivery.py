"""Security, scope, recovery and schema regression tests for the delivered app."""
from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy import inspect, select

from app.ai.base import AIResponseError, AssessmentResult
from app.config import Settings, get_settings
from app.models.password_reset import PasswordReset
from tests.conftest import auth_headers, register_and_login


def test_public_admin_registration_rejected(client):
    response = client.post('/api/auth/register', json=dict(email='admin-attempt@example.com', password='Password123!', display_name='Admin', role='admin'))
    assert response.status_code == 422


def test_final_migrated_schema(test_engine):
    schema = inspect(test_engine)
    assert set(schema.get_table_names()) == {'users', 'profiles', 'sessions', 'password_resets', 'business_ideas', 'assessments', 'alembic_version'}
    assert 'verification_status' not in {c['name'] for c in schema.get_columns('users')}
    assert 'contact_preference' not in {c['name'] for c in schema.get_columns('profiles')}


@pytest.mark.parametrize('role,info', [
    ('business_owner', {'business_name': 'Fictional GreenBox', 'industry': 'Packaging'}),
    ('innovator', {'skills': 'Design', 'experience': 'Prototyping'}),
    ('investor', {'investment_interests': 'Sustainability', 'preferred_stage': 'Idea'}),
    ('admin', {}),
])
def test_role_profile_and_dashboard(client, role, info):
    data, token = register_and_login(client, role=role)
    headers = auth_headers(token)
    assert client.put('/api/profile', headers=headers, json={'role_specific_info': info}).status_code == 200
    assert client.get('/api/profile', headers=headers).json()['role_specific_info'] == info
    assert client.put('/api/profile', headers=headers, json={'role_specific_info': {'moderation': 'yes'}}).status_code == 422
    dashboard = client.get('/api/dashboard', headers=headers).json()
    assert 'admin_actions' not in dashboard
    assert 'Sprint 2' not in str(dashboard)
    if role != 'business_owner':
        assert client.post('/api/ideas', headers=headers, json={'name': 'Forbidden'}).status_code == 403


def test_null_updates_are_validation_errors(client):
    _, token = register_and_login(client)
    headers = auth_headers(token)
    assert client.put('/api/profile', headers=headers, json={'display_name': None}).status_code == 422
    idea = client.post('/api/ideas', headers=headers, json={'name': 'Example'}).json()
    assert client.put(f"/api/ideas/{idea['id']}", headers=headers, json={'name': None}).status_code == 422
    assert client.post('/api/ideas', headers=headers, json={'name': '  '}).status_code == 422


def test_factory_failure_preserves_assessment(client, monkeypatch):
    _, token = register_and_login(client)
    headers = auth_headers(token)
    idea = client.post('/api/ideas', headers=headers, json={'name': 'Example'}).json()
    url = f"/api/ideas/{idea['id']}/assessment"
    first = client.post(url, headers=headers).json()['latest_valid']
    def fail():
        raise RuntimeError('secret provider diagnostic')
    monkeypatch.setattr('app.services.assessment.get_assessment_provider', fail)
    failed = client.post(url, headers=headers).json()
    assert failed['current_status'] == 'failed'
    assert failed['latest_valid']['id'] == first['id']
    assert 'secret' not in failed['error_message']
    assert failed['in_progress'] is False


@pytest.mark.parametrize('invalid', ['', ' ', None, 12, [], {}])
def test_blank_and_malformed_assessment_content_rejected(invalid):
    data = {key: 'Valid section' for key in AssessmentResult.model_fields}
    data['assumptions'] = invalid
    with pytest.raises(AIResponseError):
        AssessmentResult.from_mapping(data)


def test_reset_revokes_all_requests_and_sessions(client, db):
    _, token = register_and_login(client)
    one = client.post('/api/auth/password-reset/request', json={'email': 'newowner@nashaa.sa'}).json()['reset_token']
    two = client.post('/api/auth/password-reset/request', json={'email': 'newowner@nashaa.sa'}).json()['reset_token']
    assert client.post('/api/auth/password-reset/confirm', json={'token': one, 'new_password': 'Replacement123!'}).status_code == 200
    assert client.post('/api/auth/password-reset/confirm', json={'token': two, 'new_password': 'Another123!'}).status_code == 400
    assert client.get('/api/auth/me', headers=auth_headers(token)).status_code == 401
    assert all(row.token_hash not in (one, two) for row in db.scalars(select(PasswordReset)))


def test_smtp_delivery_uses_tls_and_fragment(monkeypatch):
    from app.services.mail import send_password_reset
    settings = Settings(_env_file=None, smtp_host='mail.example.com', smtp_from='no-reply@example.com', smtp_username='sender', smtp_password='secret', reset_url='https://example.com/reset-password')
    monkeypatch.setattr('app.services.mail.get_settings', lambda: settings)
    with patch('app.services.mail.smtplib.SMTP') as smtp:
        send_password_reset('fictional@example.com', 'reset-secret')
        server = smtp.return_value.__enter__.return_value
        server.starttls.assert_called_once()
        server.login.assert_called_once_with('sender', 'secret')
        message = server.send_message.call_args.args[0]
        assert message['To'] == 'fictional@example.com'
        assert 'https://example.com/reset-password#token=reset-secret' in message.get_content()


def test_production_rejects_unsafe_recovery():
    with pytest.raises(ValueError):
        Settings(_env_file=None, environment='production', smtp_host='', smtp_from='')


def test_disabled_demo_tokens_do_not_leak(client, monkeypatch):
    register_and_login(client)
    settings = get_settings().model_copy(update={'environment': 'development', 'smtp_host': 'mail.example.com', 'expose_reset_tokens': False})
    monkeypatch.setattr('app.routers.auth.get_settings', lambda: settings)
    monkeypatch.setattr('app.routers.auth.send_password_reset', lambda *args: None)
    known = client.post('/api/auth/password-reset/request', json={'email': 'newowner@nashaa.sa'}).json()
    unknown = client.post('/api/auth/password-reset/request', json={'email': 'unknown@example.com'}).json()
    assert known == unknown
    assert known['reset_token'] is None


def test_long_passwords_are_not_truncated(client):
    original = 'x' * 80 + 'a'
    register_and_login(client, password=original)
    assert client.post('/api/auth/login', json={'email': 'newowner@nashaa.sa', 'password': 'x' * 80 + 'b'}).status_code == 401


def test_later_routes_absent(client):
    paths = client.get('/api/openapi.json').json()['paths']
    for route in ('challenges', 'proposals', 'messages', 'collaborations', 'investor-matches', 'leads', 'ratings', 'reports', 'moderation', 'analytics', 'verification'):
        assert not any(route in path for path in paths)
        assert client.get('/api/' + route).status_code == 404


def test_concurrent_assessment_requests_use_database_lock(test_engine, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier, Event
    from sqlalchemy.orm import Session
    from app.ai.mock import MockAssessmentProvider
    from app.models.enums import Role
    from app.models.user import User
    from app.models.business_idea import BusinessIdea
    from app.services.auth import create_user
    from app.services.assessment import generate_assessment
    from app.services.errors import AssessmentInProgress

    start = Barrier(2)
    rejected = Event()

    class SlowProvider(MockAssessmentProvider):
        def generate(self, data):
            assert rejected.wait(10), 'Second request did not encounter the persisted lock state'
            return super().generate(data)

    monkeypatch.setattr('app.services.assessment.get_assessment_provider', SlowProvider)
    with Session(test_engine) as db:
        user = create_user(db, email='concurrency@example.com', password='Password123!', role=Role.BUSINESS_OWNER, display_name='Fictional concurrency check')
        idea = BusinessIdea(owner_id=user.id, name='Concurrent idea')
        db.add(idea)
        db.commit()
        user_id, idea_id = user.id, idea.id

    def request():
        with Session(test_engine) as db:
            user = db.get(User, user_id)
            start.wait(timeout=10)
            try:
                result = generate_assessment(db, idea_id, user)
                return result.generation_status.value
            except AssessmentInProgress:
                rejected.set()
                return 'conflict'

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: request(), range(2)))
        assert sorted(results) == ['conflict', 'succeeded']
    finally:
        with Session(test_engine) as db:
            db.delete(db.get(User, user_id))
            db.commit()
