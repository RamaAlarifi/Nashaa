"""Transparent, deterministic compatibility scoring (US15–US16)."""
from decimal import Decimal
from app.industries import industry_key


def normal(value):
    return str(value).strip().casefold()


def score(idea, preference, funding, history):
    industry = industry_key(idea.industry)
    stage = idea.business_stage.value
    if not industry or industry not in {industry_key(x) for x in preference.industries} or stage not in preference.stages:
        return None
    factors = {"industry": (35, True), "stage": (25, True)}
    missing = []
    if funding is not None:
        factors["funding"] = (20, preference.min_funding <= Decimal(funding.amount) <= preference.max_funding)
    else:
        missing.append("Project funding amount is unavailable.")
    if preference.locations and idea.target_location.strip():
        factors["location"] = (10, normal(idea.target_location) in {normal(x) for x in preference.locations})
    else:
        missing.append("Location comparison is unavailable or unrestricted.")
    if history:
        factors["history"] = (10, any(industry_key(h.industry) == industry for h in history))
    else:
        missing.append("Investment history is unavailable; current preferences were used.")
    possible = sum(weight for weight, _ in factors.values())
    return {
        "score": round(100 * sum(weight for weight, matched in factors.values() if matched) / possible, 1),
        "coverage": possible,
        "reasons": [f"{name.title()} match" for name, (_, matched) in factors.items() if matched],
        "mismatches": [f"{name.title()} does not match" for name, (_, matched) in factors.items() if not matched],
        "missing": missing,
    }
