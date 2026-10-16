"""Explicit, repeatable fictional Sprint 2 data: python -m app.seed.sprint2."""
from sqlalchemy import select
from app.config import get_settings
from app.database import SessionLocal
from app.models.enums import Role
from app.models.opportunities import Challenge, InvestmentHistory, InvestorPreference, Proposal, VerificationRequest
from app.models.user import User
from app.seed.seed import DEFAULT_PASSWORD, run_seed
from app.services.auth import create_user
from app.services.opportunity_access import now
from app.industries import canonical


def run():
    if get_settings().environment == "production":
        raise RuntimeError("Fictional seed data is disabled in production.")
    run_seed()
    with SessionLocal() as db:
        admin = db.scalar(select(User).where(User.email == "admin@nashaa.sa"))
        for index in range(1, 16):
            email = f"invest{index}@nashaa.sa"
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = create_user(db, email=email, password=DEFAULT_PASSWORD, role=Role.INVESTOR, display_name=f"Fictional investor {index}")
            if not db.scalar(select(InvestorPreference).where(InvestorPreference.user_id == user.id)):
                db.add(InvestorPreference(user_id=user.id, industries=[canonical(["Sustainable packaging", "Food and beverage", "Health tech", "Education", "Logistics"][index % 5])], stages=["idea", "validation", "early"], locations=["Riyadh", "Jeddah", "Dammam"], min_funding=10000, max_funding=500000))
            if index % 2 == 0 and not db.scalar(select(InvestmentHistory).where(InvestmentHistory.user_id == user.id)):
                db.add(InvestmentHistory(user_id=user.id, project_name=f"Fictional prior investment {index}", industry="manufacturing_packaging", stage="idea", source="Fictional Sprint 2 demonstration data"))
        for role in ("owner", "innov", "invest"):
            for index in range(1, 4):
                user = db.scalar(select(User).where(User.email == f"{role}{index}@nashaa.sa"))
                if db.scalar(select(VerificationRequest).where(VerificationRequest.user_id == user.id)):
                    continue
                status = ("approved", "pending", "rejected")[index - 1]
                user.verification_status = status
                db.add(VerificationRequest(user_id=user.id, information="Fictional professional background for Sprint 2 demonstration.", status=status, reviewer_id=admin.id if status != "pending" else None, decision_reason="Fictional platform review." if status != "pending" else "", decided_at=now() if status != "pending" else None))
        owner = db.scalar(select(User).where(User.email == "owner1@nashaa.sa"))
        innovator = db.scalar(select(User).where(User.email == "innov1@nashaa.sa"))
        for index in range(1, 11):
            title = f"Fictional Sprint 2 challenge {index}"
            if db.scalar(select(Challenge).where(Challenge.owner_id == owner.id, Challenge.title == title)):
                continue
            row = Challenge(owner_id=owner.id, title=title, problem="Reduce packaging waste for a fictional small restaurant.", desired_outcome="A practical reusable packaging prototype.", required_skills=["Design", "Prototyping"], industry="manufacturing_packaging", location="Riyadh", timeline="4 weeks", compensation="Scope to be agreed", status="draft" if index == 10 else "published", approved_at=None if index == 10 else now())
            db.add(row); db.flush()
            if index <= 3:
                db.add(Proposal(challenge_id=row.id, innovator_id=innovator.id, approach="Develop and test a reusable packaging prototype.", deliverables="Design files, prototype and testing notes.", timeline="4 weeks", cost=5000))
        db.commit()
    print("Fictional Sprint 2 data ready: 15 investor profiles and 10 challenges. Existing entries retained.")


if __name__ == "__main__":
    run()
