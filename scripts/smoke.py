"""HTTP acceptance checks against a disposable Docker stack with mock AI.

Usage: python scripts/smoke.py http://localhost:3100 --demo-reset
Creates fictional test accounts/ideas. Never target a real deployment.
"""
import json
import sys
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError

base = sys.argv[1].rstrip('/').replace('localhost', '127.0.0.1')
suffix = uuid.uuid4().hex[:10]


def call(path, body=None, token=None, method=None, expected=200):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = Request(base + path, data=json.dumps(body).encode() if body is not None else None, headers=headers, method=method)
    try:
        response = urlopen(req, timeout=90)
    except HTTPError as error:
        response = error
    assert response.status == expected, (path, response.status, expected)
    raw = response.read()
    if 'application/json' in response.headers.get('Content-Type', ''):
        return json.loads(raw) if raw else None
    return raw.decode()


for page in ('/', '/register', '/login', '/forgot-password', '/reset-password', '/dashboard', '/profile', '/ideas', '/ideas/new'):
    call(page)
for asset in ('logo.svg', 'logo-reversed.svg', 'logo-tagline.svg', 'logo-mark.svg', 'icon.svg', 'favicon.svg'):
    assert '<svg' in call('/brand/' + asset)
assert call('/api/health')['status'] == 'ok'
sessions = {}
for role in ('business_owner', 'innovator', 'investor'):
    account = call('/api/auth/register', {'email': f'{role}-{suffix}@example.com', 'password': 'FictionalPass123!', 'role': role, 'display_name': 'Fictional QA'}, expected=201)
    sessions[role] = account['token']
    assert call('/api/dashboard', token=account['token'])['role'] == role
    assert call('/api/profile', token=account['token'])['display_name'] == 'Fictional QA'
owner = sessions['business_owner']
viewer = sessions['investor']
idea = call('/api/ideas', {'name': 'Fictional smoke idea', 'problem': 'Packaging waste', 'solution': 'Reusable boxes', 'target_location': 'Riyadh'}, token=owner, expected=201)
path = '/api/ideas/' + idea['id']
call(path, token=viewer, expected=404)
call(path + '/visibility', {'visibility': 'registered'}, owner, 'PATCH')
summary = call(path, token=viewer)
assert 'problem' not in summary and 'budget' not in summary
call(path + '/assessment', token=viewer, expected=404)
call(path, {'problem': 'Unauthorized'}, viewer, 'PUT', expected=404)
call('/api/ideas', {'name': 'Not allowed'}, viewer, expected=403)
first = call(path + '/assessment', {}, owner)['latest_valid']
assert all(first[key] for key in ('market_considerations', 'target_customer_analysis', 'competitor_considerations', 'indicative_costs', 'suggested_next_steps', 'assumptions'))
edited = call(path, {'problem': 'Updated fictional packaging problem'}, owner, 'PUT')
assert edited['revision_number'] == 2
latest = call(path + '/assessment', {}, owner)['latest_valid']
assert latest['idea_revision'] == 2 and latest['id'] != first['id']
if '--demo-reset' in sys.argv:
    reset = call('/api/auth/password-reset/request', {'email': f'business_owner-{suffix}@example.com'})['reset_token']
    assert reset
    call('/api/auth/password-reset/confirm', {'token': reset, 'new_password': 'Replacement123!'})
    call('/api/auth/me', token=owner, expected=401)
    call('/api/auth/password-reset/confirm', {'token': reset, 'new_password': 'Replacement456!'}, expected=400)
    owner = call('/api/auth/login', {'email': f'business_owner-{suffix}@example.com', 'password': 'Replacement123!'})['token']
call('/api/auth/logout', {}, owner, expected=204)
call('/api/auth/me', token=owner, expected=401)
for route in ('challenges', 'proposals', 'messages', 'collaborations', 'investor-matches', 'leads', 'ratings', 'reports', 'moderation', 'analytics', 'verification'):
    call('/api/' + route, expected=404)
    call('/' + route, expected=404)
print('PASS: pages/assets, same-origin API, accounts, profiles, dashboards, ideas, assessment regeneration, visibility, ownership, logout and absent later routes')
if '--demo-reset' in sys.argv:
    print('PASS: reset link, single-use reset, session revocation and new-password login')
