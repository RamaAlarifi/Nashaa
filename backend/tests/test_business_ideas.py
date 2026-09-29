"""US05 â€” create, save, reopen, and edit a business idea; revision tracking."""

from __future__ import annotations

from tests.conftest import auth_headers, register_and_login

VALID_IDEA = {
    "name": "GreenBox",
    "problem": "Small restaurants need affordable eco packaging.",
    "solution": "Biodegradable packaging from local waste.",
    "industry": "Sustainable packaging",
    "business_stage": "idea",
    "target_location": "Riyadh",
    "intended_customers": "Independent restaurants and cafes",
    "budget": "SAR 50000",
    "current_challenges": "High raw material cost.",
    "visibility": "private",
}


def _create(client, token, **overrides):
    payload = {**VALID_IDEA, **overrides}
    return client.post("/api/ideas", json=payload, headers=auth_headers(token))


def test_create_idea_owner_only(client):
    # Innovator cannot create (403).
    _, innov_token = register_and_login(client, email="nope@nashaa.sa",
                                        role="innovator", display_name="N")
    res = client.post("/api/ideas", json=VALID_IDEA, headers=auth_headers(innov_token))
    assert res.status_code == 403


def test_create_valid_idea(client):
    _, token = register_and_login(client, email="ci@nashaa.sa", display_name="CI")
    res = _create(client, token)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["name"] == "GreenBox"
    assert body["owner_id"]  # connected to the owner
    assert body["revision_number"] == 1
    assert body["visibility"] == "private"


def test_create_invalid_idea_missing_name(client):
    _, token = register_and_login(client, email="inv@nashaa.sa", display_name="INV")
    payload = {**VALID_IDEA, "name": ""}
    res = client.post("/api/ideas", json=payload, headers=auth_headers(token))
    assert res.status_code == 422


def test_create_invalid_business_stage(client):
    _, token = register_and_login(client, email="bs@nashaa.sa", display_name="BS")
    payload = {**VALID_IDEA, "business_stage": "not-a-stage"}
    res = client.post("/api/ideas", json=payload, headers=auth_headers(token))
    assert res.status_code == 422


def test_save_and_reopen_idea(client):
    _, token = register_and_login(client, email="sr@nashaa.sa", display_name="SR")
    idea_id = _create(client, token).json()["id"]

    res = client.get("/api/ideas", headers=auth_headers(token))
    assert res.status_code == 200
    assert any(i["id"] == idea_id for i in res.json())

    res2 = client.get(f"/api/ideas/{idea_id}", headers=auth_headers(token))
    assert res2.status_code == 200
    assert res2.json()["name"] == "GreenBox"


def test_edit_assessment_related_field_increases_revision(client):
    _, token = register_and_login(client, email="rev@nashaa.sa", display_name="REV")
    idea_id = _create(client, token).json()["id"]
    assert client.get(f"/api/ideas/{idea_id}", headers=auth_headers(token)).json()["revision_number"] == 1

    res = client.put(
        f"/api/ideas/{idea_id}",
        json={"problem": "A different problem statement."},
        headers=auth_headers(token),
    )
    assert res.status_code == 200
    assert res.json()["revision_number"] == 2


def test_edit_name_increases_revision(client):
    _, token = register_and_login(client, email="rev2@nashaa.sa", display_name="REV2")
    idea_id = _create(client, token).json()["id"]

    res = client.put(
        f"/api/ideas/{idea_id}",
        json={"name": "GreenBox Renamed"},
        headers=auth_headers(token),
    )
    assert res.status_code == 200
    assert res.json()["name"] == "GreenBox Renamed"
    assert res.json()["revision_number"] == 2  # name is included in the assessment input


def test_edit_visibility_does_not_increase_revision(client):
    _, token = register_and_login(client, email="rev3@nashaa.sa", display_name="REV3")
    idea_id = _create(client, token).json()["id"]
    res = client.patch(
        f"/api/ideas/{idea_id}/visibility",
        json={"visibility": "registered"},
        headers=auth_headers(token),
    )
    assert res.status_code == 200
    assert res.json()["visibility"] == "registered"
    assert res.json()["revision_number"] == 1


def test_attempt_to_edit_another_users_idea(client):
    _, token_a = register_and_login(client, email="ea@nashaa.sa", display_name="EA")
    _, token_b = register_and_login(client, email="eb@nashaa.sa", display_name="EB")
    idea_id = _create(client, token_a).json()["id"]

    res = client.put(
        f"/api/ideas/{idea_id}",
        json={"problem": "hijack"},
        headers=auth_headers(token_b),
    )
    # 404 to avoid leaking the existence of someone else's private record.
    assert res.status_code == 404


def test_attempt_to_delete_another_users_idea(client):
    _, token_a = register_and_login(client, email="da@nashaa.sa", display_name="DA")
    _, token_b = register_and_login(client, email="db@nashaa.sa", display_name="DB")
    idea_id = _create(client, token_a).json()["id"]
    res = client.delete(f"/api/ideas/{idea_id}", headers=auth_headers(token_b))
    assert res.status_code == 404
    # Still exists for the owner.
    assert client.get(f"/api/ideas/{idea_id}", headers=auth_headers(token_a)).status_code == 200


def test_delete_own_idea(client):
    _, token = register_and_login(client, email="del@nashaa.sa", display_name="DEL")
    idea_id = _create(client, token).json()["id"]
    res = client.delete(f"/api/ideas/{idea_id}", headers=auth_headers(token))
    assert res.status_code == 204
    assert client.get(f"/api/ideas/{idea_id}", headers=auth_headers(token)).status_code == 404
