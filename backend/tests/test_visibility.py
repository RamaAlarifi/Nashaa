"""US08 â€” idea visibility, enforced by the server on every request."""

from __future__ import annotations

from tests.conftest import auth_headers, register_and_login

VALID_IDEA = {
    "name": "PrivateIdea", "problem": "P", "solution": "S", "industry": "Tech",
    "business_stage": "idea", "target_location": "Riyadh", "intended_customers": "SMBs",
    "budget": "SAR 1", "current_challenges": "C", "visibility": "private",
}


def _create(client, token, **overrides):
    return client.post("/api/ideas", json={**VALID_IDEA, **overrides}, headers=auth_headers(token))


def test_private_idea_hidden_from_other_users(client):
    _, token_a = register_and_login(client, email="pv_a@nashaa.sa", display_name="A")
    _, token_b = register_and_login(client, email="pv_b@nashaa.sa", display_name="B")
    idea_id = _create(client, token_a, visibility="private").json()["id"]

    # Other user cannot view it (404 hides existence).
    res = client.get(f"/api/ideas/{idea_id}", headers=auth_headers(token_b))
    assert res.status_code == 404
    # Owner still sees full detail.
    res2 = client.get(f"/api/ideas/{idea_id}", headers=auth_headers(token_a))
    assert res2.status_code == 200
    assert res2.json()["problem"] == "P"  # full access


def test_registered_idea_shows_summary_to_others(client):
    _, token_a = register_and_login(client, email="rg_a@nashaa.sa", display_name="A")
    _, token_b = register_and_login(client, email="rg_b@nashaa.sa", display_name="B")
    idea_id = _create(client, token_a, visibility="registered").json()["id"]

    res = client.get(f"/api/ideas/{idea_id}", headers=auth_headers(token_b))
    assert res.status_code == 200
    body = res.json()
    # Summary fields present...
    assert body["name"] == "PrivateIdea"
    assert body["industry"] == "Tech"
    # ...but sensitive detail fields are NOT exposed to non-owners.
    assert "problem" not in body
    assert "solution" not in body
    assert "current_challenges" not in body
    assert "budget" not in body


def test_visibility_setting_is_saved(client):
    _, token = register_and_login(client, email="vs@nashaa.sa", display_name="VS")
    idea_id = _create(client, token, visibility="private").json()["id"]

    res = client.patch(
        f"/api/ideas/{idea_id}/visibility",
        json={"visibility": "registered"},
        headers=auth_headers(token),
    )
    assert res.status_code == 200
    assert res.json()["visibility"] == "registered"
    # Persists on reopen.
    assert client.get(f"/api/ideas/{idea_id}", headers=auth_headers(token)).json()["visibility"] == "registered"


def test_browse_only_lists_registered_ideas(client):
    _, token_a = register_and_login(client, email="br_a@nashaa.sa", display_name="A")
    _, token_b = register_and_login(client, email="br_b@nashaa.sa", display_name="B")
    private_id = _create(client, token_a, name="Hidden", visibility="private").json()["id"]
    public_id = _create(client, token_a, name="Shown", visibility="registered").json()["id"]

    res = client.get("/api/ideas/browse", headers=auth_headers(token_b))
    assert res.status_code == 200
    ids = [i["id"] for i in res.json()]
    assert public_id in ids
    assert private_id not in ids


def test_visibility_checked_by_server_even_via_direct_request(client):
    """A signed-in user cannot read another owner's private idea by calling the
    endpoint directly with the id (server enforces on every request)."""
    _, token_a = register_and_login(client, email="sx_a@nashaa.sa", display_name="A")
    _, token_b = register_and_login(client, email="sx_b@nashaa.sa", display_name="B")
    idea_id = _create(client, token_a, visibility="private").json()["id"]
    res = client.get(f"/api/ideas/{idea_id}", headers=auth_headers(token_b))
    assert res.status_code == 404
