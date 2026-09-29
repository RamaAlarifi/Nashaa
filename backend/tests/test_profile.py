"""US03 â€” maintain a profile; role cannot be changed via profile update."""

from __future__ import annotations

from tests.conftest import auth_headers, register_and_login


def test_get_own_profile(client):
    _, token = register_and_login(client, email="p1@nashaa.sa", display_name="ProfileOne")
    res = client.get("/api/profile", headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json()["display_name"] == "ProfileOne"


def test_update_own_profile_persists(client):
    _, token = register_and_login(client, email="p2@nashaa.sa", display_name="ProfileTwo")
    res = client.put(
        "/api/profile",
        json={"display_name": "ProfileTwo-Updated", "location": "Jeddah",
              "short_description": "Founder"},
        headers=auth_headers(token),
    )
    assert res.status_code == 200
    assert res.json()["display_name"] == "ProfileTwo-Updated"
    assert res.json()["location"] == "Jeddah"

    # Reopen profile: changes persist.
    res2 = client.get("/api/profile", headers=auth_headers(token))
    assert res2.json()["display_name"] == "ProfileTwo-Updated"
    assert res2.json()["location"] == "Jeddah"


def test_role_cannot_be_changed_through_profile_update(client):
    _, token = register_and_login(client, email="p3@nashaa.sa",
                                  role="business_owner", display_name="P3")
    # Attempt to smuggle a role change.
    res = client.put(
        "/api/profile",
        json={"display_name": "P3-updated", "role": "admin"},
        headers=auth_headers(token),
    )
    assert res.status_code == 200
    # Role is unchanged.
    me = client.get("/api/auth/me", headers=auth_headers(token)).json()
    assert me["user"]["role"] == "business_owner"


def test_profile_update_isolated_between_users(client):
    _, token_a = register_and_login(client, email="a@nashaa.sa", display_name="Alpha")
    _, token_b = register_and_login(client, email="b@nashaa.sa", display_name="Bravo")

    # User A updates their own profile only.
    client.put("/api/profile", json={"display_name": "Alpha-X"}, headers=auth_headers(token_a))

    # User B's profile is untouched.
    res = client.get("/api/profile", headers=auth_headers(token_b))
    assert res.json()["display_name"] == "Bravo"


def test_view_other_user_private_profile_blocked(client):
    _, token_a = register_and_login(client, email="vp_a@nashaa.sa", display_name="VA")
    a_id = client.get("/api/auth/me", headers=auth_headers(token_a)).json()["user"]["id"]

    # Make A's profile private.
    client.put("/api/profile", json={"profile_visibility": "private"}, headers=auth_headers(token_a))

    _, token_b = register_and_login(client, email="vp_b@nashaa.sa", display_name="VB")
    res = client.get(f"/api/users/{a_id}/profile", headers=auth_headers(token_b))
    assert res.status_code == 403


def test_view_other_user_registered_profile_allowed(client):
    _, token_a = register_and_login(client, email="rp_a@nashaa.sa", display_name="RA")
    a_id = client.get("/api/auth/me", headers=auth_headers(token_a)).json()["user"]["id"]

    _, token_b = register_and_login(client, email="rp_b@nashaa.sa", display_name="RB")
    res = client.get(f"/api/users/{a_id}/profile", headers=auth_headers(token_b))
    assert res.status_code == 200
    assert res.json()["display_name"] == "RA"
