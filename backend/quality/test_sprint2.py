"""Executed requirements coverage for US09–US16 and approved sharing."""
from decimal import Decimal
from types import SimpleNamespace as NS
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.models.enums import BusinessStage
from app.schemas.opportunities import ContactIn, FundingIn, MessageIn, PreferenceIn, ProposalIn, ShareIn, VerificationIn
from app.services.matching import score
from quality.conftest import auth_headers, register_and_login

CHALLENGE = dict(title="Packaging challenge", problem="Reduce packaging waste", desired_outcome="A reusable packaging design", required_skills=["Design"], industry="Packaging", location="Riyadh", timeline="4 weeks", compensation="Discuss scope first")
PROPOSAL = dict(approach="Prototype reusable packaging", deliverables="Design and tested prototype", timeline="4 weeks", cost="5000.00")
PREFERENCE = dict(industries=["Packaging"], stages=["idea"], locations=["Riyadh"], min_funding="1000", max_funding="100000")


@pytest.fixture
def actors(client):
    result = {}
    for name, role in [("owner", "business_owner"), ("innovator", "innovator"), ("investor", "investor"), ("admin", "admin")]:
        data, token = register_and_login(client, email=f"s2-{name}@example.com", role=role, display_name=f"Fictional {name}")
        result[name] = {"id": data["user"]["id"], "headers": auth_headers(token)}
    return result


def approved(client, actors, role):
    response = client.post("/api/verification", headers=actors[role]["headers"], json={"information": "Fictional professional background for prototype verification."})
    assert response.status_code == 201, response.text
    response = client.post(f"/api/admin/verification/{response.json()['id']}/decision", headers=actors["admin"]["headers"], json={"decision": "approved", "reason": "Fictional demonstration review approved."})
    assert response.status_code == 200, response.text


def challenge(client, actors, publish=True):
    response = client.post("/api/challenges", headers=actors["owner"]["headers"], json=CHALLENGE)
    assert response.status_code == 201, response.text
    row = response.json()
    if publish:
        response = client.post(f"/api/challenges/{row['id']}/publish", headers=actors["owner"]["headers"], json={"approved": True})
        assert response.status_code == 200, response.text
    return row


def shared_setup(client, actors):
    headers = actors["owner"]["headers"]
    idea = client.post("/api/ideas", headers=headers, json={"name": "Fictional GreenBox", "industry": "Packaging", "visibility": "registered", "problem": "Packaging waste", "solution": "Reuse packaging"}).json()
    assessment = client.post(f"/api/ideas/{idea['id']}/assessment", headers=headers).json()["latest_valid"]
    assert assessment is not None
    share = client.post(f"/api/ideas/{idea['id']}/assessment-shares", headers=headers, json={"assessment_id": assessment["id"], "investor_id": actors["investor"]["id"], "approved": True})
    assert share.status_code == 201, share.text
    return idea, assessment, share.json()


@pytest.mark.parametrize("model,payload", [
    (MessageIn, {"body": " "}), (MessageIn, {"body": "a" * 4001}),
    (ProposalIn, {**PROPOSAL, "approach": "short"}), (ProposalIn, {**PROPOSAL, "deliverables": ""}),
    (ProposalIn, {**PROPOSAL, "cost": "-0.01"}), (ProposalIn, {**PROPOSAL, "cost": "1.001"}),
    (PreferenceIn, {**PREFERENCE, "min_funding": "100001"}), (PreferenceIn, {**PREFERENCE, "industries": []}),
    (PreferenceIn, {**PREFERENCE, "stages": ["unknown"]}), (FundingIn, {"amount": "-1"}),
    (FundingIn, {"amount": "10", "currency": "USD"}), (VerificationIn, {"information": "short"}),
    (ContactIn, {"recipient_id": "00000000-0000-0000-0000-000000000001"}),
    (ShareIn, {"assessment_id": "00000000-0000-0000-0000-000000000001", "investor_id": "00000000-0000-0000-0000-000000000002", "approved": False}),
    (MessageIn, {"body": "valid", "sender_id": "spoof"}),
])
def test_unit_invalid_commands(model, payload):
    with pytest.raises(ValidationError):
        model.model_validate(payload)


@pytest.mark.parametrize("amount,expected", [("1000", True), ("100000", True), ("999.99", False), ("100000.01", False)])
def test_unit_matching_funding_boundaries(amount, expected):
    idea = NS(industry=" packaging ", business_stage=BusinessStage.IDEA, target_location="Riyadh")
    pref = NS(**{**PREFERENCE, "min_funding": Decimal("1000"), "max_funding": Decimal("100000")})
    result = score(idea, pref, NS(amount=Decimal(amount)), [])
    assert ("Funding match" in result["reasons"]) is expected
    assert result["coverage"] == 90
    assert any("history" in x for x in result["missing"])


def test_unit_missing_optional_data_and_mismatch():
    idea = NS(industry="Packaging", business_stage=BusinessStage.IDEA, target_location="")
    pref = NS(**PREFERENCE)
    result = score(idea, pref, None, [])
    assert result["score"] == 100 and result["coverage"] == 60 and len(result["missing"]) == 3
    idea.industry = "Health"
    assert score(idea, pref, None, []) is None


def test_verification_decisions_and_reapplication(client, actors):
    h = actors["innovator"]["headers"]
    first = client.post("/api/verification", headers=h, json={"information": "Fictional professional background for review."})
    assert first.status_code == 201
    path = f"/api/admin/verification/{first.json()['id']}/decision"
    assert client.post(path, headers=h, json={"decision": "approved", "reason": "Self approval attempt"}).status_code == 403
    assert client.post("/api/verification", headers=h, json={"information": "A duplicate fictional pending request."}).status_code == 409
    assert client.post(path, headers=actors["admin"]["headers"], json={"decision": "rejected", "reason": "Please provide more relevant background."}).status_code == 200
    status = client.get("/api/verification", headers=h).json()
    assert status["status"] == "rejected" and status["requests"][0]["decision_reason"]
    approved(client, actors, "innovator")
    assert client.get("/api/auth/me", headers=h).json()["user"]["verification_status"] == "approved"


def test_challenge_lifecycle_and_filters(client, actors):
    h = actors["owner"]["headers"]; other = actors["innovator"]["headers"]
    row = challenge(client, actors, False); path = f"/api/challenges/{row['id']}"
    assert client.get("/api/challenges", headers=other).json() == []
    assert client.get(path, headers=other).status_code == 404
    assert client.post(path + "/publish", headers=h, json={"approved": False}).status_code == 422
    assert client.post(path + "/publish", headers=h, json={"approved": True}).status_code == 200
    assert len(client.get("/api/challenges?industry=pack&skill=design&location=riyadh", headers=other).json()) == 1
    assert client.get("/api/challenges?skill=accounting", headers=other).json() == []
    assert client.put(path, headers=h, json={**CHALLENGE, "title": "Reviewed change"}).json()["status"] == "draft"
    assert client.post(path + "/publish", headers=h, json={"approved": True}).status_code == 200
    assert client.post(path + "/close", headers=h).json()["status"] == "closed"
    assert client.get("/api/challenges", headers=other).json() == []


def test_challenge_input_and_ownership(client, actors):
    h = actors["owner"]["headers"]
    assert client.post("/api/challenges", headers=actors["investor"]["headers"], json=CHALLENGE).status_code == 403
    row = client.post("/api/challenges", headers=h, json={"title": "Incomplete draft"}).json()
    assert client.post(f"/api/challenges/{row['id']}/publish", headers=h, json={"approved": True}).status_code == 422
    _, token = register_and_login(client, email="other-owner@example.com")
    assert client.put(f"/api/challenges/{row['id']}", headers=auth_headers(token), json=CHALLENGE).status_code == 404


def test_proposal_gates_duplicates_and_selection(client, actors):
    row = challenge(client, actors); path = f"/api/challenges/{row['id']}"
    ih = actors["innovator"]["headers"]; oh = actors["owner"]["headers"]
    assert client.post(path + "/proposals", headers=ih, json=PROPOSAL).status_code == 403
    approved(client, actors, "innovator")
    proposal = client.post(path + "/proposals", headers=ih, json=PROPOSAL)
    assert proposal.status_code == 201
    assert proposal.json()["innovator_id"] == actors["innovator"]["id"]
    assert client.post(path + "/proposals", headers=ih, json=PROPOSAL).status_code == 409
    assert client.put(path, headers=oh, json=CHALLENGE).status_code == 409
    other = challenge(client, actors)
    assert client.post(f"/api/challenges/{other['id']}/select/{proposal.json()['id']}", headers=oh).status_code == 404
    selection = path + "/select/" + proposal.json()["id"]
    assert client.post(selection, headers=ih).status_code == 403
    assert client.post(selection, headers=oh).status_code == 201
    assert client.post(selection, headers=oh).status_code == 409
    assert client.post(path + "/proposals", headers=ih, json=PROPOSAL).status_code == 409
    assert client.get("/api/proposals", headers=ih).json()[0]["status"] == "selected"


def test_system_challenge_to_conversation(client, actors):
    approved(client, actors, "owner"); approved(client, actors, "innovator")
    c = challenge(client, actors); path = f"/api/challenges/{c['id']}"
    p = client.post(path + "/proposals", headers=actors["innovator"]["headers"], json=PROPOSAL).json()
    assert client.post(path + "/select/" + p["id"], headers=actors["owner"]["headers"]).status_code == 201
    request = client.post("/api/contact-requests", headers=actors["owner"]["headers"], json={"recipient_id": actors["innovator"]["id"], "challenge_id": c["id"]})
    assert request.status_code == 201, request.text
    assert request.json()["status"] == "pending"
    assert client.post(f"/api/contact-requests/{request.json()['id']}/decision", headers=actors["innovator"]["headers"], json={"decision": "accepted"}).status_code == 200
    threads = client.get("/api/conversations", headers=actors["owner"]["headers"]).json()
    assert len(threads) == 1
    messages = f"/api/conversations/{threads[0]['id']}/messages"
    assert client.post(messages, headers=actors["owner"]["headers"], json={"body": "Let us agree on the first design review."}).status_code == 201
    assert client.get(messages, headers=actors["innovator"]["headers"]).json()[0]["body"].startswith("Let us")
    assert client.get(messages, headers=actors["investor"]["headers"]).status_code == 404
    assert client.post(messages, headers=actors["owner"]["headers"], json={"body": " "}).status_code == 422
    assert client.post(f"/api/contact-requests/{request.json()['id']}/decision", headers=actors["owner"]["headers"], json={"decision": "revoked"}).status_code == 200
    assert client.get(messages, headers=actors["innovator"]["headers"]).status_code == 403
    assert client.post(messages, headers=actors["owner"]["headers"], json={"body": "Blocked after revocation"}).status_code == 403


def test_contact_open_closed_and_restored_permission(client, actors):
    approved(client, actors, "owner"); approved(client, actors, "innovator")
    c = challenge(client, actors)
    oh, ih = actors["owner"]["headers"], actors["innovator"]["headers"]
    payload = {"recipient_id": actors["innovator"]["id"], "challenge_id": c["id"]}
    assert client.put("/api/contact-preference", headers=ih, json={"preference": "closed"}).status_code == 200
    assert client.post("/api/contact-requests", headers=oh, json=payload).status_code == 403
    client.put("/api/contact-preference", headers=ih, json={"preference": "open"})
    request = client.post("/api/contact-requests", headers=oh, json=payload).json()
    assert request["status"] == "accepted"
    first = client.get("/api/conversations", headers=oh).json()[0]
    client.post(f"/api/contact-requests/{request['id']}/decision", headers=ih, json={"decision": "revoked"})
    assert client.post("/api/contact-requests", headers=oh, json=payload).status_code == 201
    second = client.get("/api/conversations", headers=oh).json()
    assert len(second) == 1 and second[0]["id"] == first["id"]
    assert client.get(f"/api/conversations/{first['id']}/messages", headers=oh).status_code == 200


def test_investment_history_matching_and_visibility(client, actors):
    ih, oh = actors["investor"]["headers"], actors["owner"]["headers"]
    idea = client.post("/api/ideas", headers=oh, json={"name": "Packaging", "industry": "Packaging", "visibility": "registered"}).json()
    assert client.put("/api/investor-preferences", headers=ih, json=PREFERENCE).status_code == 200
    funding_result = client.put(f"/api/ideas/{idea['id']}/funding", headers=oh, json={"amount": "5000.01"})
    assert funding_result.status_code == 200 and funding_result.json()["amount"] == "5000.01"
    assert client.get("/api/investor-preferences", headers=ih).json()["min_funding"] == "1000.00"
    feed = client.get("/api/investor/projects", headers=ih).json()
    assert len(feed) == 1 and feed[0]["missing"]
    assert "problem" not in feed[0]["idea"] and "budget" not in feed[0]["idea"]
    h = client.post("/api/investment-history", headers=ih, json={"project_name": "Fictional previous project", "industry": "Packaging", "stage": "idea", "source": "Fictional demonstration history"}).json()
    _, other_token = register_and_login(client, email="history-outsider@example.com", role="investor")
    assert client.delete(f"/api/investment-history/{h['id']}", headers=auth_headers(other_token)).status_code == 404
    assert client.put("/api/investor-preferences", headers=oh, json=PREFERENCE).status_code == 403
    assert client.get("/api/investor/projects", headers=ih).json()[0]["coverage"] > feed[0]["coverage"]
    assert client.put(f"/api/investment-history/{h['id']}", headers=ih, json={"project_name": "Updated fictional project", "industry": "Health", "stage": "early", "source": "Self-reported fictional history"}).status_code == 200
    assert client.delete(f"/api/investment-history/{h['id']}", headers=ih).status_code == 204
    assert client.get(f"/api/ideas/{idea['id']}/investor-matches", headers=oh).json()
    client.patch(f"/api/ideas/{idea['id']}/visibility", headers=oh, json={"visibility": "private"})
    assert client.get("/api/investor/projects", headers=ih).json() == []


@pytest.mark.parametrize("visibility_method", ["PUT", "PATCH"])
def test_system_explicit_sharing_version_privacy_and_revocation(client, actors, visibility_method):
    idea, assessment, grant = shared_setup(client, actors)
    oh, ih = actors["owner"]["headers"], actors["investor"]["headers"]
    path = f"/api/assessment-shares/{grant['id']}"
    response = client.get(path, headers=ih)
    assert response.status_code == 200
    assert "input_snapshot" not in response.text and "error_message" not in response.text
    assert client.get(path, headers=actors["innovator"]["headers"]).status_code == 403
    assert client.get(f"/api/ideas/{idea['id']}/assessment", headers=ih).status_code == 404
    assert client.get(f"/api/ideas/{idea['id']}/assessment-versions", headers=ih).status_code == 404
    new = client.post(f"/api/ideas/{idea['id']}/assessment", headers=oh).json()["latest_valid"]
    assert new["id"] != assessment["id"]
    versions = client.get(f"/api/ideas/{idea['id']}/assessment-versions", headers=oh).json()
    assert [v["id"] for v in versions] == [new["id"], assessment["id"]]
    assert client.get(path, headers=ih).json()["assessment"]["id"] == assessment["id"]
    visibility_path = f"/api/ideas/{idea['id']}" + ("/visibility" if visibility_method == "PATCH" else "")
    assert client.request(visibility_method, visibility_path, headers=oh, json={"visibility": "private"}).status_code == 200
    assert client.get(path, headers=ih).status_code == 404
    client.request(visibility_method, visibility_path, headers=oh, json={"visibility": "registered"})
    assert client.get(path, headers=ih).status_code == 404
    assert client.get("/api/assessment-shares", headers=ih).json() == []


def test_sharing_manual_revoke_and_deletion_history(client, actors):
    idea, _, grant = shared_setup(client, actors)
    oh, ih = actors["owner"]["headers"], actors["investor"]["headers"]
    assert client.delete(f"/api/assessment-shares/{grant['id']}", headers=ih).status_code == 404
    assert client.delete(f"/api/assessment-shares/{grant['id']}", headers=oh).status_code == 200
    assert client.get(f"/api/assessment-shares/{grant['id']}", headers=ih).status_code == 404
    assert client.delete(f"/api/ideas/{idea['id']}", headers=oh).status_code == 409


def test_share_recipient_is_specific_and_private_idea_cannot_be_shared(client, actors):
    idea, assessment, grant = shared_setup(client, actors)
    _, token = register_and_login(client, email="other-investor@example.com", role="investor")
    assert client.get(f"/api/assessment-shares/{grant['id']}", headers=auth_headers(token)).status_code == 404
    oh = actors["owner"]["headers"]
    client.patch(f"/api/ideas/{idea['id']}/visibility", headers=oh, json={"visibility": "private"})
    assert client.post(f"/api/ideas/{idea['id']}/assessment-shares", headers=oh, json={"assessment_id": assessment["id"], "investor_id": actors["investor"]["id"], "approved": True}).status_code == 409


def test_contact_cannot_be_self_approved_or_accessed_by_outsider(client, actors):
    approved(client, actors, "owner"); approved(client, actors, "innovator")
    c = challenge(client, actors)
    request = client.post("/api/contact-requests", headers=actors["owner"]["headers"], json={"recipient_id": actors["innovator"]["id"], "challenge_id": c["id"]}).json()
    path = f"/api/contact-requests/{request['id']}/decision"
    assert client.post(path, headers=actors["owner"]["headers"], json={"decision": "accepted"}).status_code == 403
    assert client.post(path, headers=actors["investor"]["headers"], json={"decision": "revoked"}).status_code == 404
    assert client.get("/api/contact-requests", headers=actors["investor"]["headers"]).json() == []


def test_inactive_account_login_rejected(client, actors, db):
    from app.models.enums import AccountStatus
    from app.models.user import User
    user = db.get(User, UUID(actors["owner"]["id"]))
    user.account_status = AccountStatus.SUSPENDED
    db.commit()
    assert client.post("/api/auth/login", json={"email": "s2-owner@example.com", "password": "Password123!"}).status_code == 403


@pytest.mark.parametrize("path", ["/verification", "/challenges", "/proposals", "/contact-requests", "/conversations", "/investor-preferences", "/investment-history", "/investor/projects", "/assessment-shares", "/admin/verification"])
def test_sprint2_requires_session(client, path):
    assert client.get("/api" + path).status_code == 401
