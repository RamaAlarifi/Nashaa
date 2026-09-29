"""Mock assessment provider.

Returns a clearly-labeled, valid, structured assessment derived from the
input. Used when no real API key is configured or for offline tests. The
output is explicitly marked as simulated so it is never mistaken for a real
AI result (project rule: clearly identify AI assumptions and uncertain
information).
"""

from __future__ import annotations

from app.ai.base import AssessmentInput, AssessmentProvider, AssessmentResult


class MockAssessmentProvider(AssessmentProvider):
    name = "mock"

    def generate(self, data: AssessmentInput) -> AssessmentResult:
        stage_label = data.business_stage.value.replace("_", " ").title()

        market = (
            f"Simulated market overview for the '{data.name}' idea in the "
            f"{data.industry or 'unspecified'} sector. Demand appears to depend "
            f"on the size of the {data.target_location or 'target'} market and "
            f"early adopter willingness to pay. This is an illustrative mock "
            f"analysis, not a real market study."
        )
        customers = (
            f"Likely customers: {data.intended_customers or 'not specified'}. "
            f"At the {stage_label} stage, focus on a narrow early segment and "
            f"validate willingness to pay before expanding. (Simulated.)"
        )
        competitors = (
            f"Potential competitors include established players in "
            f"{data.industry or 'this space'} and indirect substitutes. A real "
            f"competitor scan is recommended. (Simulated.)"
        )
        costs = (
            f"Indicative cost areas: product development, operations, and "
            f"customer acquisition. Stated budget: {data.budget or 'not stated'}. "
            f"Build a simple cost model and revisit. (Simulated.)"
        )
        next_steps = (
            "1. Validate the core problem with 10+ target customers.\n"
            "2. Build a minimal version of the solution.\n"
            "3. Define 2-3 measurable success metrics.\n"
            "4. Plan a small launch in the target location.\n"
            "(Simulated next steps.)"
        )
        assumptions = (
            "ASSUMPTIONS (simulated): these conclusions are illustrative and "
            "based only on the information you provided. They are not financial, "
            "legal, or market advice. Verify every assumption before acting."
        )
        sources = "No external sources used. This is a simulated assessment."

        return AssessmentResult(
            market_considerations=market,
            target_customer_analysis=customers,
            competitor_considerations=competitors,
            indicative_costs=costs,
            suggested_next_steps=next_steps,
            assumptions=assumptions,
            sources=sources,
        )
