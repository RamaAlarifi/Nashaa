"""US06 & US07 â€” AI assessment generation, failure protection, and concurrency.

Covers:
- successful assessment (mock provider)
- AI service failure (provider raises) -> failed status, useful message,
  previous successful result preserved
- invalid AI response structure -> failed status
- delayed AI response -> slow provider still completes successfully; an
  in-progress attempt is reflected in the status
- assessment update after editing an idea records the new idea revision
- two assessment requests cannot run at the same time (in-progress guard -> 409)
"""

from __future__ import annotations

import time

from app.ai.base import (
    AIResponseError,
    AIServiceError,
    AssessmentInput,
    AssessmentProvider,
    AssessmentResult,
)
from app.models.assessment import Assessment
from app.models.enums import AssessmentStatus
from tests.conftest import auth_headers, register_and_login

VALID_IDEA = {
    "name": "GreenBox", "problem": "P", "solution": "S", "industry": "Sustainable packaging",
    "business_stage": "idea", "target_location": "Riyadh",
    "intended_customers": "Restaurants", "budget": "SAR 50000",
    "current_challenges": "Cost", "visibility": "private",
}


def _create_idea(client, token):
    return client.post("/api/ideas", json=VALID_IDEA, headers=auth_headers(token)).json()["id"]


# ---------- Custom providers ----------

class _FailingProvider(AssessmentProvider):
    def generate(self, data: AssessmentInput) -> AssessmentResult:
        raise AIServiceError("The AI service is temporarily unavailable.")


class _InvalidProvider(AssessmentProvider):
    def generate(self, data: AssessmentInput) -> AssessmentResult:
        raise AIResponseError("AI response missing required fields: ['market_considerations']")


class _SlowProvider(AssessmentProvider):
    def generate(self, data: AssessmentInput) -> AssessmentResult:
        time.sleep(0.3)  # simulate a delayed response
        return AssessmentResult(
            market_considerations="m", target_customer_analysis="t",
            competitor_considerations="c", indicative_costs="i",
            suggested_next_steps="s", assumptions="a", sources="",
        )


# ---------- Tests ----------

def test_successful_assessment(client):
    _, token = register_and_login(client, email="as_ok@nashaa.sa", display_name="OK")
    idea_id = _create_idea(client, token)

    res = client.post(f"/api/ideas/{idea_id}/assessment", headers=auth_headers(token))
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["current_status"] == "succeeded"
    assert body["in_progress"] is False
    assert body["latest_valid"] is not None
    valid = body["latest_valid"]
    # US06 required fields are populated.
    assert valid["market_considerations"]
    assert valid["target_customer_analysis"]
    assert valid["competitor_considerations"]
    assert valid["indicative_costs"]
    assert valid["suggested_next_steps"]
    assert valid["assumptions"]  # assumptions clearly present
    assert valid["idea_revision"] == 1


def test_ai_service_failure_keeps_previous_result(client, with_ai_provider):
    _, token = register_and_login(client, email="as_fail@nashaa.sa", display_name="FAIL")
    idea_id = _create_idea(client, token)

    # First: a successful assessment.
    first = client.post(f"/api/ideas/{idea_id}/assessment", headers=auth_headers(token))
    assert first.json()["current_status"] == "succeeded"
    first_valid_text = first.json()["latest_valid"]["market_considerations"]

    # Now the provider fails.
    with_ai_provider(_FailingProvider())
    second = client.post(f"/api/ideas/{idea_id}/assessment", headers=auth_headers(token))
    assert second.status_code == 200
    body = second.json()
    assert body["current_status"] == "failed"
    assert body["error_message"]
    # The previous successful result is preserved.
    assert body["latest_valid"] is not None
    assert body["latest_valid"]["market_considerations"] == first_valid_text


def test_invalid_ai_response_structure(client, with_ai_provider):
    _, token = register_and_login(client, email="as_inv@nashaa.sa", display_name="INV")
    idea_id = _create_idea(client, token)
    with_ai_provider(_InvalidProvider())
    res = client.post(f"/api/ideas/{idea_id}/assessment", headers=auth_headers(token))
    assert res.status_code == 200
    body = res.json()
    assert body["current_status"] == "failed"
    assert body["latest_valid"] is None  # no prior success to keep
    assert body["error_message"]


def test_assessment_update_after_edit_records_new_revision(client):
    _, token = register_and_login(client, email="as_rev@nashaa.sa", display_name="REV")
    idea_id = _create_idea(client, token)

    first = client.post(f"/api/ideas/{idea_id}/assessment", headers=auth_headers(token))
    assert first.json()["latest_valid"]["idea_revision"] == 1

    # Edit an assessment-related field -> revision becomes 2.
    client.put(f"/api/ideas/{idea_id}", json={"problem": "new problem"},
              headers=auth_headers(token))
    assert client.get(f"/api/ideas/{idea_id}", headers=auth_headers(token)).json()["revision_number"] == 2

    second = client.post(f"/api/ideas/{idea_id}/assessment", headers=auth_headers(token))
    assert second.json()["latest_valid"]["idea_revision"] == 2


def test_delayed_ai_response_completes(client, with_ai_provider):
    _, token = register_and_login(client, email="as_slow@nashaa.sa", display_name="SLOW")
    idea_id = _create_idea(client, token)
    with_ai_provider(_SlowProvider())
    start = time.time()
    res = client.post(f"/api/ideas/{idea_id}/assessment", headers=auth_headers(token))
    elapsed = time.time() - start
    assert res.status_code == 200
    assert res.json()["current_status"] == "succeeded"
    assert elapsed >= 0.3  # the delayed provider was actually used


def test_in_progress_status_reflected(client, db, with_ai_provider):
    _, token = register_and_login(client, email="as_prog@nashaa.sa", display_name="PROG")
    idea_id = _create_idea(client, token)

    # Simulate a generation already in flight by inserting an IN_PROGRESS row.
    in_flight = Assessment(
        idea_id=idea_id, idea_revision=1, input_snapshot={},
        generation_status=AssessmentStatus.IN_PROGRESS,
    )
    db.add(in_flight)
    db.commit()

    res = client.get(f"/api/ideas/{idea_id}/assessment", headers=auth_headers(token))
    assert res.status_code == 200
    body = res.json()
    assert body["current_status"] == "in_progress"
    assert body["in_progress"] is True


def test_two_concurrent_requests_blocked(client, db):
    """When a generation is already in progress, a second request is rejected
    (409), so two requests cannot accidentally run for the same idea at once."""
    _, token = register_and_login(client, email="as_2x@nashaa.sa", display_name="TWO")
    idea_id = _create_idea(client, token)

    in_flight = Assessment(
        idea_id=idea_id, idea_revision=1, input_snapshot={},
        generation_status=AssessmentStatus.IN_PROGRESS,
    )
    db.add(in_flight)
    db.commit()

    res = client.post(f"/api/ideas/{idea_id}/assessment", headers=auth_headers(token))
    assert res.status_code == 409
    assert "already" in res.json()["detail"].lower()


def test_assessment_owner_only(client):
    _, token_a = register_and_login(client, email="as_a@nashaa.sa", display_name="A")
    _, token_b = register_and_login(client, email="as_b@nashaa.sa", display_name="B")
    idea_id = _create_idea(client, token_a)

    # Another user cannot request or view the assessment.
    assert client.post(f"/api/ideas/{idea_id}/assessment", headers=auth_headers(token_b)).status_code == 404
    assert client.get(f"/api/ideas/{idea_id}/assessment", headers=auth_headers(token_b)).status_code == 404
