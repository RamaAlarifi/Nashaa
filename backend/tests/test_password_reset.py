"""US02 â€” password reset with limited-time, single-use tokens.

Reset secrets are stored only as SHA-256 hashes. Tokens are single-use and
time-limited. Expired and used tokens are rejected.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.core.security import generate_token, hash_token
from app.models.password_reset import PasswordReset
from tests.conftest import auth_headers, register_and_login


def _make_reset(db, user_id, *, expired=False, used=False, token=None):
    token = token or generate_token()
    now = datetime.now(timezone.utc)
    expires = now - timedelta(minutes=10) if expired else now + timedelta(minutes=25)
    reset = PasswordReset(
        user_id=user_id,
        token_hash=hash_token(token),
        expires_at=expires,
        used_at=(now - timedelta(minutes=5)) if used else None,
    )
    db.add(reset)
    db.commit()
    return token


def test_reset_request_returns_token_in_testing(client):
    register_and_login(client, email="r@nashaa.sa", display_name="R")
    res = client.post("/api/auth/password-reset/request", json={"email": "r@nashaa.sa"})
    assert res.status_code == 200
    body = res.json()
    assert body["reset_token"]  # populated because ENVIRONMENT != production


def test_reset_request_unknown_email_does_not_leak(client):
    res = client.post("/api/auth/password-reset/request", json={"email": "ghost@nashaa.sa"})
    assert res.status_code == 200
    assert res.json()["reset_token"] is None


def test_reset_with_valid_token_changes_password(client, db):
    data, _ = register_and_login(
        client, email="v@nashaa.sa", password="Password123!", display_name="V"
    )
    user_id = data["user"]["id"]
    token = _make_reset(db, user_id)

    res = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": token, "new_password": "NewPass123!"},
    )
    assert res.status_code == 200, res.text

    # Old password no longer works.
    res_old = client.post(
        "/api/auth/login", json={"email": "v@nashaa.sa", "password": "Password123!"}
    )
    assert res_old.status_code == 401
    # New password works.
    res_new = client.post(
        "/api/auth/login", json={"email": "v@nashaa.sa", "password": "NewPass123!"}
    )
    assert res_new.status_code == 200


def test_reset_with_expired_token_rejected(client, db):
    data, _ = register_and_login(client, email="e@nashaa.sa", display_name="E")
    token = _make_reset(db, data["user"]["id"], expired=True)
    res = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": token, "new_password": "NewPass123!"},
    )
    assert res.status_code == 400


def test_reset_with_used_token_cannot_be_reused(client, db):
    data, _ = register_and_login(client, email="u@nashaa.sa", display_name="U")
    token = _make_reset(db, data["user"]["id"], used=True)
    res = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": token, "new_password": "NewPass123!"},
    )
    assert res.status_code == 400


def test_reset_with_invalid_token_rejected(client):
    res = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": "totally-invalid-token", "new_password": "NewPass123!"},
    )
    assert res.status_code == 400


def test_valid_reset_token_becomes_used_after_success(client, db):
    data, _ = register_and_login(client, email="w@nashaa.sa", display_name="W")
    token = _make_reset(db, data["user"]["id"])
    # First use succeeds.
    res = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": token, "new_password": "NewPass123!"},
    )
    assert res.status_code == 200
    # Second use fails (single-use).
    res2 = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": token, "new_password": "AnotherPass1!"},
    )
    assert res2.status_code == 400


def test_reset_token_hashed_not_stored_plaintext(db, client):
    data, _ = register_and_login(client, email="h@nashaa.sa", display_name="H")
    token = _make_reset(db, data["user"]["id"])
    row = db.query(PasswordReset).filter_by(token_hash=hash_token(token)).one()
    assert row.token_hash != token  # only the hash is stored
