"""Seed Nashaa with fictional demonstration data (Sprint 1).

This script creates:
  - 16 test accounts across the four roles (US01 ready to log in)
  - 12 fictional Saudi business ideas in different industries and stages,
    with a mix of private / registered visibility and some incomplete ideas
  - successful and failed fictional assessments (US06/US07)
Password reset edge cases and delayed responses live in the isolated tests.

Run with:
    python -m app.seed.seed

All data is clearly fictional. Do not use real personal data in demonstrations
(project rule 11 + section 17).
"""

from __future__ import annotations

from sqlalchemy import select

from app.database import SessionLocal
from app.config import get_settings
from app.models.assessment import Assessment
from app.models.business_idea import BusinessIdea
from app.models.enums import (
    AssessmentStatus,
    BusinessStage,
    IdeaVisibility,
    ProfileVisibility,
    Role,
)
from app.models.user import User
from app.core.security import hash_password

DEFAULT_PASSWORD = "Password123!"


# (email, role, display_name, location, description, visibility)
USERS = [
    ("admin@nashaa.sa", Role.ADMIN, "Platform Admin", "Riyadh",
     "Nashaa platform administrator.", ProfileVisibility.PRIVATE),
    ("owner1@nashaa.sa", Role.BUSINESS_OWNER, "Layla Al-Otaibi", "Riyadh",
     "Restaurant owner exploring sustainable packaging.", ProfileVisibility.REGISTERED),
    ("owner2@nashaa.sa", Role.BUSINESS_OWNER, "Khalid Al-Harbi", "Jeddah",
     "Logistics startup founder.", ProfileVisibility.REGISTERED),
    ("owner3@nashaa.sa", Role.BUSINESS_OWNER, "Noura Al-Qahtani", "Dammam",
     "Health-tech entrepreneur.", ProfileVisibility.PUBLIC),
    ("owner4@nashaa.sa", Role.BUSINESS_OWNER, "Faisal Al-Dossari", "Riyadh",
     "Education services for kids.", ProfileVisibility.REGISTERED),
    ("owner5@nashaa.sa", Role.BUSINESS_OWNER, "Sara Al-Mutairi", "Mecca",
     "E-commerce handmade goods.", ProfileVisibility.REGISTERED),
    ("innov1@nashaa.sa", Role.INNOVATOR, "Omar Al-Shehri", "Riyadh",
     "Full-stack developer.", ProfileVisibility.REGISTERED),
    ("innov2@nashaa.sa", Role.INNOVATOR, "Mona Al-Zahrani", "Jeddah",
     "UX/UI designer.", ProfileVisibility.REGISTERED),
    ("innov3@nashaa.sa", Role.INNOVATOR, "Tariq Al-Ghamdi", "Dammam",
     "Cloud and DevOps consultant.", ProfileVisibility.REGISTERED),
    ("innov4@nashaa.sa", Role.INNOVATOR, "Hala Al-Subaie", "Riyadh",
     "Mobile app developer.", ProfileVisibility.REGISTERED),
    ("innov5@nashaa.sa", Role.INNOVATOR, "Yousef Al-Anazi", "Medina",
     "Marketing and growth specialist.", ProfileVisibility.REGISTERED),
    ("invest1@nashaa.sa", Role.INVESTOR, "Reem Al-Maliki", "Riyadh",
     "Angel investor, sustainability focus.", ProfileVisibility.REGISTERED),
    ("invest2@nashaa.sa", Role.INVESTOR, "Abdullah Al-Asmari", "Jeddah",
     "Venture capital, logistics and SaaS.", ProfileVisibility.REGISTERED),
    ("invest3@nashaa.sa", Role.INVESTOR, "Maha Al-Naimi", "Dammam",
     "Health and education angel investor.", ProfileVisibility.REGISTERED),
    ("invest4@nashaa.sa", Role.INVESTOR, "Sultan Al-Rashidi", "Riyadh",
     "Early-stage retail and e-commerce investor.", ProfileVisibility.REGISTERED),
    ("invest5@nashaa.sa", Role.INVESTOR, "Dana Al-Faris", "Mecca",
     "Impact investor, women-led businesses.", ProfileVisibility.REGISTERED),
]


# (owner_email, name, problem, solution, industry, stage, location, customers, budget, challenges, visibility, revision)
IDEAS = [
    ("owner1@nashaa.sa", "GreenBox", "Small restaurants need affordable environmentally friendly packaging.",
     "Biodegradable packaging made from local agricultural waste.", "Sustainable packaging",
     BusinessStage.IDEA, "Riyadh", "Independent restaurants and cafes", "SAR 50,000",
     "High cost of raw materials; limited supplier options.", IdeaVisibility.PRIVATE, 1),
    ("owner2@nashaa.sa", "QuickRoute", "Last-mile delivery is slow and expensive for small sellers.",
     "A shared-route delivery app for small e-commerce sellers.", "Logistics",
     BusinessStage.VALIDATION, "Jeddah", "Small online sellers", "SAR 120,000",
     "Driver recruitment; competition with large platforms.", IdeaVisibility.REGISTERED, 2),
    ("owner3@nashaa.sa", "CareLine", "Patients forget follow-up appointments after clinic visits.",
     "Automated, localized appointment reminders and check-ins.", "Health tech",
     BusinessStage.EARLY, "Dammam", "Primary care clinics", "SAR 200,000",
     "Data privacy rules; integration with clinic systems.", IdeaVisibility.REGISTERED, 1),
    ("owner4@nashaa.sa", "LittleMinds", "Parents lack affordable after-school coding activities.",
     "Weekly coding clubs for kids aged 8-12, delivered online.", "Education",
     BusinessStage.IDEA, "Riyadh", "Parents of primary-school children", "SAR 80,000",
     "Finding qualified instructors; retention after free trial.", IdeaVisibility.PRIVATE, 1),
    ("owner5@nashaa.sa", "SaudiHands", "Handcraft makers struggle to sell online.",
     "A curated marketplace for Saudi handmade products.", "E-commerce",
     BusinessStage.OPERATING, "Mecca", "Local artisans and buyers", "SAR 75,000",
     "Logistics for rural makers; quality control.", IdeaVisibility.REGISTERED, 3),
    ("owner1@nashaa.sa", "FreshBite", "Office workers lack healthy lunch options nearby.",
     "Daily healthy meal subscription delivered to offices.", "Food and beverage",
     BusinessStage.IDEA, "Riyadh", "Office workers", "SAR 100,000",
     "Kitchen capacity; perishable inventory.", IdeaVisibility.REGISTERED, 1),
    ("owner2@nashaa.sa", "FarmDirect", "Small farms cannot reach urban buyers directly.",
     "A farm-to-table platform connecting farmers and retailers.", "Agriculture",
     BusinessStage.IDEA, "Qassim", "Small farmers and city grocers", "SAR 150,000",
     "Cold chain logistics; farmer digital literacy.", IdeaVisibility.PRIVATE, 1),
    ("owner3@nashaa.sa", "MediTrack", "Clinics lose track of medical supplies and expiry dates.",
     "A simple inventory system for small clinics.", "Health tech",
     BusinessStage.VALIDATION, "Dammam", "Small private clinics", "SAR 90,000",
     "User training; integration effort.", IdeaVisibility.REGISTERED, 1),
    ("owner4@nashaa.sa", "EduMate", "Students need affordable tutoring help.",
     "On-demand tutoring matching platform for school subjects.", "Education",
     BusinessStage.IDEA, "Riyadh", "School students and parents", "SAR 60,000",
     "Tutor quality control; pricing.", IdeaVisibility.REGISTERED, 1),
    ("owner5@nashaa.sa", "BoutiqueHub", "Small fashion brands need affordable online stores.",
     "A low-cost storefront builder for micro fashion brands.", "Retail tech",
     BusinessStage.IDEA, "Mecca", "Micro fashion brands", "SAR 40,000",
     "Standing out vs. large platforms.", IdeaVisibility.PRIVATE, 1),
    ("owner1@nashaa.sa", "WaterWise", "Restaurants waste water and overpay on bills.",
     "", "Sustainability", BusinessStage.IDEA, "Riyadh", "Restaurants", "SAR 35,000",
     "", IdeaVisibility.REGISTERED, 1),  # incomplete: missing solution & challenges
    ("owner3@nashaa.sa", "ClinicBook", "Clinics double-book appointment slots.",
     "A lightweight calendar with conflict detection for clinics.", "Health tech",
     BusinessStage.SCALING, "Dammam", "Clinics", "SAR 250,000",
     "Scaling support team; multi-branch needs.", IdeaVisibility.REGISTERED, 1),
]


def _get_user(db, email: str) -> User:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def _create_users(db) -> dict[str, User]:
    created: dict[str, User] = {}
    for email, role, name, location, desc, vis in USERS:
        existing = _get_user(db, email)
        if existing is not None:
            created[email] = existing
            continue
        from app.models.profile import Profile

        user = User(
            email=email,
            password_hash=hash_password(DEFAULT_PASSWORD),
            role=role,
        )
        Profile(
            user=user,
            display_name=name,
            location=location,
            short_description=desc,
            role_specific_info={},
            profile_visibility=vis,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        created[email] = user
    return created


def _create_ideas(db, users: dict[str, User]) -> dict[str, BusinessIdea]:
    created: dict[str, BusinessIdea] = {}
    for spec in IDEAS:
        (owner_email, name, problem, solution, industry, stage, loc, cust, budget, challenges, vis, revision) = spec
        owner = users[owner_email]
        existing = db.execute(select(BusinessIdea).where(BusinessIdea.owner_id == owner.id, BusinessIdea.name == name)).scalar_one_or_none()
        if existing is not None:
            continue
        idea = BusinessIdea(
            owner_id=owner.id,
            name=name,
            problem=problem,
            solution=solution,
            industry=industry,
            business_stage=stage,
            target_location=loc,
            intended_customers=cust,
            budget=budget,
            current_challenges=challenges,
            visibility=vis,
            revision_number=revision,
        )
        db.add(idea)
        db.commit()
        db.refresh(idea)
        created[name] = idea
    return created


def _create_assessments(db, ideas: dict[str, BusinessIdea]) -> None:
    from app.ai.mock import MockAssessmentProvider

    mock = MockAssessmentProvider()
    from app.ai.base import AssessmentInput

    if not all(name in ideas for name in ("GreenBox", "SaudiHands", "QuickRoute", "CareLine")):
        return

    # Successful assessment for GreenBox (revision 1).
    idea = ideas["GreenBox"]
    inp = AssessmentInput(
        name=idea.name, problem=idea.problem, solution=idea.solution, industry=idea.industry,
        business_stage=idea.business_stage, target_location=idea.target_location,
        intended_customers=idea.intended_customers, budget=idea.budget, current_challenges=idea.current_challenges,
    )
    result = mock.generate(inp)
    a1 = Assessment(
        idea_id=idea.id, idea_revision=idea.revision_number,
        input_snapshot={"name": idea.name}, generation_status=AssessmentStatus.SUCCEEDED,
        market_considerations=result.market_considerations,
        target_customer_analysis=result.target_customer_analysis,
        competitor_considerations=result.competitor_considerations,
        indicative_costs=result.indicative_costs,
        suggested_next_steps=result.suggested_next_steps,
        assumptions=result.assumptions, sources=result.sources,
    )
    db.add(a1)

    # Successful assessment for SaudiHands (revision 3 â€” reflects prior edits).
    idea2 = ideas["SaudiHands"]
    inp2 = AssessmentInput(
        name=idea2.name, problem=idea2.problem, solution=idea2.solution, industry=idea2.industry,
        business_stage=idea2.business_stage, target_location=idea2.target_location,
        intended_customers=idea2.intended_customers, budget=idea2.budget, current_challenges=idea2.current_challenges,
    )
    result2 = mock.generate(inp2)
    a2 = Assessment(
        idea_id=idea2.id, idea_revision=idea2.revision_number,
        input_snapshot={"name": idea2.name}, generation_status=AssessmentStatus.SUCCEEDED,
        market_considerations=result2.market_considerations,
        target_customer_analysis=result2.target_customer_analysis,
        competitor_considerations=result2.competitor_considerations,
        indicative_costs=result2.indicative_costs,
        suggested_next_steps=result2.suggested_next_steps,
        assumptions=result2.assumptions, sources=result2.sources,
    )
    db.add(a2)

    # Failed assessment for QuickRoute (previous attempt; shows a useful message).
    a3 = Assessment(
        idea_id=ideas["QuickRoute"].id, idea_revision=ideas["QuickRoute"].revision_number,
        input_snapshot={"name": "QuickRoute"}, generation_status=AssessmentStatus.FAILED,
        error_message="The AI service is temporarily unavailable. Please try again.",
    )
    db.add(a3)

    # Interrupted fictional attempt; the owner can regenerate immediately.
    a4 = Assessment(
        idea_id=ideas["CareLine"].id, idea_revision=ideas["CareLine"].revision_number,
        input_snapshot={"name": "CareLine"}, generation_status=AssessmentStatus.FAILED,
        error_message="Fictional interrupted attempt. Generate an assessment to continue.",
    )
    db.add(a4)
    db.commit()


def run_seed() -> dict:
    """Create all seed data. Idempotent: existing users are kept."""
    if get_settings().environment == "production":
        raise RuntimeError("Fictional seed data is disabled in production.")
    db = SessionLocal()
    try:
        users = _create_users(db)
        ideas = _create_ideas(db, users)
        if ideas:
            _create_assessments(db, ideas)
        tokens = {}
    finally:
        db.close()
    return {"users": len(users), "ideas": len(ideas), "reset_tokens": tokens}


def main() -> None:
    summary = run_seed()
    print("Nashaa seed complete.")
    print(f"  Users: {summary['users']}  | Ideas: {summary['ideas']}")



if __name__ == "__main__":
    main()
