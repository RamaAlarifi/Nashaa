"""US04 â€” role-based dashboards; role restrictions cannot be bypassed by
calling endpoints directly (server checks every protected action)."""

from __future__ import annotations

from tests.conftest import auth_headers, register_and_login


def _create_idea(client, token, name="My Idea"):
    return client.post(
        "/api/ideas",
        json={
            "name": name, "problem": "P", "solution": "S", "industry": "Tech",
            "business_stage": "idea", "target_location": "Riyadh",
            "intended_customers": "SMBs", "budget": "SAR 50000",
            "current_challenges": "C", "visibility": "private",
        },
        headers=auth_headers(token),
    )


def test_business_owner_dashboard_shows_ideas(client):
    _, token = register_and_login(client, email="dash_owner@nashaa.sa", display_name="Owner")
    _create_idea(client, token, name="Idea A")
    res = client.get("/api/dashboard", headers=auth_headers(token))
    assert res.status_code == 200
    body = res.json()
    assert body["role"] == "business_owner"
    assert body["ideas"] is not None
    assert len(body["ideas"]) == 1
    assert body["ideas"][0]["name"] == "Idea A"
    assert body["ideas"][0]["assessment_status"] == "none"


def test_innovator_dashboard_basic(client):
    _, token = register_and_login(client, email="dash_innov@nashaa.sa",
                                  role="innovator", display_name="Innov")
    res = client.get("/api/dashboard", headers=auth_headers(token))
    body = res.json()
    assert body["role"] == "innovator"
    assert body["ideas"] is None
    assert body["message"]


def test_investor_dashboard_basic(client):
    _, token = register_and_login(client, email="dash_inv@nashaa.sa",
                                  role="investor", display_name="Inv")
    res = client.get("/api/dashboard", headers=auth_headers(token))
    body = res.json()
    assert body["role"] == "investor"
    assert body["ideas"] is None
    assert body["message"]


def test_admin_dashboard_basic(client):
    _, token = register_and_login(client, email="dash_admin@nashaa.sa",
                                  role="admin", display_name="Admin")
    res = client.get("/api/dashboard", headers=auth_headers(token))
    body = res.json()
    assert body["role"] == "admin"
    assert body["message"]
    assert "admin_actions" not in body


def test_role_restriction_not_bypassed_by_direct_request(client):
    """An innovator cannot create a business idea by POSTing directly (the
    server checks the role, not just the screen)."""
    _, token = register_and_login(client, email="bypass@nashaa.sa",
                                  role="innovator", display_name="Bypass")
    res = client.post(
        "/api/ideas",
        json={"name": "X", "problem": "P", "solution": "S", "industry": "Tech",
              "business_stage": "idea", "target_location": "Riyadh",
              "intended_customers": "SMBs", "budget": "SAR 1", "current_challenges": "C",
              "visibility": "private"},
        headers=auth_headers(token),
    )
    assert res.status_code == 403


def test_role_restriction_investor_cannot_create_idea(client):
    _, token = register_and_login(client, email="inv_create@nashaa.sa",
                                  role="investor", display_name="InvC")
    res = client.post(
        "/api/ideas",
        json={"name": "X", "problem": "P", "solution": "S", "industry": "Tech",
              "business_stage": "idea", "target_location": "Riyadh",
              "intended_customers": "SMBs", "budget": "SAR 1", "current_challenges": "C",
              "visibility": "private"},
        headers=auth_headers(token),
    )
    assert res.status_code == 403


def test_dashboard_requires_authentication(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 401
