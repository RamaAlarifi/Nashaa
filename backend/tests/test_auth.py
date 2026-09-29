"""US01 â€” register, login, logout, and the personal workspace (/me)."""

from __future__ import annotations

from tests.conftest import auth_headers, register_and_login


def test_register_success(client):
    res = client.post(
        "/api/auth/register",
        json={
            "email": "founder@nashaa.sa",
            "password": "Password123!",
            "role": "business_owner",
            "display_name": "Layla",
        },
    )
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["token"]
    assert data["token_type"] == "Bearer"
    assert data["user"]["email"] == "founder@nashaa.sa"
    assert data["user"]["role"] == "business_owner"
    assert data["profile"]["display_name"] == "Layla"


def test_register_creates_profile(client):
    data, _ = register_and_login(client, email="p@nashaa.sa", display_name="P")
    assert data["profile"] is not None
    assert data["profile"]["display_name"] == "P"


def test_register_invalid_email_rejected(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "Password123!",
              "role": "business_owner", "display_name": "X"},
    )
    assert res.status_code == 422


def test_register_short_password_rejected(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "short@nashaa.sa", "password": "123",
              "role": "business_owner", "display_name": "X"},
    )
    assert res.status_code == 422


def test_register_duplicate_email_rejected(client):
    register_and_login(client, email="dup@nashaa.sa", display_name="Dup")
    res = client.post(
        "/api/auth/register",
        json={"email": "dup@nashaa.sa", "password": "Password123!",
              "role": "business_owner", "display_name": "Other"},
    )
    assert res.status_code == 409


def test_login_success(client):
    register_and_login(client, email="login@nashaa.sa", password="Password123!",
                       display_name="Login")
    res = client.post(
        "/api/auth/login",
        json={"email": "login@nashaa.sa", "password": "Password123!"},
    )
    assert res.status_code == 200
    assert res.json()["token"]


def test_login_wrong_password(client):
    register_and_login(client, email="lp@nashaa.sa", password="Password123!",
                       display_name="LP")
    res = client.post(
        "/api/auth/login",
        json={"email": "lp@nashaa.sa", "password": "WrongPassword1"},
    )
    assert res.status_code == 401


def test_login_unknown_user_rejected(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "ghost@nashaa.sa", "password": "Password123!"},
    )
    assert res.status_code == 401


def test_me_requires_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_returns_user_and_profile(client):
    data, token = register_and_login(client, email="me@nashaa.sa", display_name="Me")
    res = client.get("/api/auth/me", headers=auth_headers(token))
    assert res.status_code == 200
    body = res.json()
    assert body["user"]["email"] == "me@nashaa.sa"
    assert body["profile"]["display_name"] == "Me"


def test_logout_ends_session(client):
    _, token = register_and_login(client, email="out@nashaa.sa", display_name="Out")
    # Before logout, /me works.
    assert client.get("/api/auth/me", headers=auth_headers(token)).status_code == 200
    # Logout.
    res = client.post("/api/auth/logout", headers=auth_headers(token))
    assert res.status_code == 204
    # After logout, the token is invalid.
    assert client.get("/api/auth/me", headers=auth_headers(token)).status_code == 401


def test_invalid_token_rejected(client):
    res = client.get("/api/auth/me", headers=auth_headers("not-a-real-token"))
    assert res.status_code == 401
