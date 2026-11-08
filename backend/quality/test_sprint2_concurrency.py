"""Real PostgreSQL sessions race for one challenge, not mocked locks."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.enums import Role
from app.models.opportunities import Challenge, Collaboration, Proposal
from app.models.user import User
from app.services.auth import create_user
from app.services.challenges import close, select_proposal, submit
from app.schemas.opportunities import ProposalIn
from app.schemas.business_idea import BusinessIdeaUpdate


def test_two_selections_create_one_collaboration(test_engine):
    suffix = uuid4().hex
    with Session(test_engine) as db:
        users = []
        for index, role in enumerate([Role.BUSINESS_OWNER, Role.INNOVATOR, Role.INNOVATOR]):
            user = create_user(db, email=f"race-{index}-{suffix}@example.com", password="Password123!", role=role, display_name="Fictional selection race")
            user.verification_status = "approved"; users.append(user)
        c = Challenge(owner_id=users[0].id, title="Concurrent challenge", status="published")
        db.add(c); db.flush()
        proposals = [Proposal(challenge_id=c.id, innovator_id=u.id, approach="Valid approach", deliverables="Valid deliverables", timeline="4 weeks") for u in users[1:]]
        db.add_all(proposals); db.commit()
        owner_id, challenge_id, ids = users[0].id, c.id, [p.id for p in proposals]
    barrier = Barrier(2)
    def choose(proposal_id):
        with Session(test_engine) as db:
            owner = db.get(User, owner_id); barrier.wait(10)
            try:
                select_proposal(db, owner, challenge_id, proposal_id)
                return "selected"
            except HTTPException as error:
                assert error.status_code == 409
                return "conflict"
    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(choose, ids)) == ["conflict", "selected"]
    with Session(test_engine) as db:
        assert db.scalar(select(func.count()).select_from(Collaboration).where(Collaboration.challenge_id == challenge_id)) == 1


def test_close_and_submit_are_serialised(test_engine):
    suffix = uuid4().hex
    with Session(test_engine) as db:
        owner = create_user(db, email=f"close-owner-{suffix}@example.com", password="Password123!", role=Role.BUSINESS_OWNER, display_name="Fictional owner")
        innovator = create_user(db, email=f"close-innovator-{suffix}@example.com", password="Password123!", role=Role.INNOVATOR, display_name="Fictional innovator")
        innovator.verification_status = "approved"
        c = Challenge(owner_id=owner.id, title="Closing challenge", status="published")
        db.add(c); db.commit(); owner_id, innovator_id, challenge_id = owner.id, innovator.id, c.id
    barrier = Barrier(2)
    def run(action):
        with Session(test_engine) as db:
            user = db.get(User, owner_id if action == "close" else innovator_id); barrier.wait(10)
            try:
                if action == "close": close(db, user, challenge_id)
                else: submit(db, user, challenge_id, ProposalIn(approach="A valid approach", deliverables="A valid deliverable", timeline="2 weeks"))
                return "ok"
            except HTTPException as error:
                assert action == "submit" and error.status_code == 409
                return "conflict"
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(run, ["close", "submit"]))
    assert results[0] == "ok" and results[1] in ("ok", "conflict")
    with Session(test_engine) as db:
        assert db.get(Challenge, challenge_id).status == "closed"
        count = db.scalar(select(func.count()).select_from(Proposal).where(Proposal.challenge_id == challenge_id))
        assert count == (1 if results[1] == "ok" else 0)


def test_locked_idea_refreshes_preloaded_revision(test_engine):
    from app.models.business_idea import BusinessIdea
    from app.services.business_ideas import update_idea
    from app.services.assessment import generate_assessment
    with Session(test_engine) as db:
        owner = create_user(db, email=f"stale-{uuid4().hex}@example.com", password="Password123!", role=Role.BUSINESS_OWNER, display_name="Fictional stale-state test")
        idea = BusinessIdea(owner_id=owner.id, name="Before update")
        db.add(idea); db.commit(); owner_id, idea_id = owner.id, idea.id
    with Session(test_engine) as old, Session(test_engine) as newer:
        owner = old.get(User, owner_id)
        assert old.get(BusinessIdea, idea_id).revision_number == 1
        update_idea(newer, idea_id, newer.get(User, owner_id), BusinessIdeaUpdate(name="Saved elsewhere"))
        result = update_idea(old, idea_id, owner, BusinessIdeaUpdate(problem="Additional update"))
        assert result.revision_number == 3 and result.name == "Saved elsewhere"
        update_idea(newer, idea_id, newer.get(User, owner_id), BusinessIdeaUpdate(solution="Newer saved solution"))
        assessment = generate_assessment(old, idea_id, owner)
        assert assessment.idea_revision == 4
        assert assessment.input_snapshot["solution"] == "Newer saved solution"
