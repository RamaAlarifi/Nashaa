"use client";
import { useParams } from "next/navigation";
import { Alert } from "@/components/States";
import { LoadState, Section, useResource } from "@/components/OpportunityUI";
import type { SharedAssessment } from "@/lib/opportunity-types";
const sections = { market_considerations: "Market considerations", target_customer_analysis: "Target customers", competitor_considerations: "Competitor considerations", indicative_costs: "Indicative costs", suggested_next_steps: "Suggested next steps", assumptions: "Assumptions", sources: "Sources" } as const;
export default function SharedAssessmentPage() {
  const { id } = useParams<{ id: string }>(); const r = useResource<SharedAssessment>(`/assessment-shares/${id}`);
  return <div className="space-y-6"><h1 className="text-3xl font-semibold">Owner-approved assessment</h1><LoadState {...r} retry={r.reload} />{r.data && <><p>{r.data.idea.name} · assessment revision {r.data.assessment.idea_revision} · {r.data.assessment.provider === "gemini" ? "Gemini" : r.data.assessment.provider === "mock" ? "Simulated output" : "Provider not recorded"}</p>{r.data.stale && <Alert kind="info" message="The idea has changed since this assessment was generated. The owner shared this specific earlier version." />}{Object.entries(sections).map(([key, title]) => <Section key={key} title={title}><p className="whitespace-pre-wrap">{r.data!.assessment[key as keyof typeof sections] || "Not provided"}</p></Section>)}</>}</div>;
}
