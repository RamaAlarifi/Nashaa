"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Action, ActionForm, LoadState, MatchDetails, Section, useResource } from "./OpportunityUI";
import { Alert } from "./States";
import { Select } from "./Input";
import type { Assessment, BusinessIdea } from "@/lib/types";
import type { Match, Share, SharedAssessment } from "@/lib/opportunity-types";

export function IdeaOpportunities({ idea, assessment: latest }: { idea: BusinessIdea; assessment: Assessment | null | undefined }) {
  const path = `/ideas/${idea.id}`;
  const funding = useResource<{ amount: string }>(`${path}/funding`);
  const matches = useResource<Match[]>(`${path}/investor-matches`);
  const shares = useResource<Share[]>(`${path}/assessment-shares`);
  const investors = useResource<{ id: string; name: string }[]>("/investors");
  const versions = useResource<SharedAssessment["assessment"][]>(`${path}/assessment-versions`);
  const [selectedVersion, setSelectedVersion] = useState("");
  useEffect(() => { void versions.reload(); }, [latest?.id, versions.reload]);
  const assessment = versions.data?.find(v => v.id === selectedVersion) ?? latest;
  async function reload() { await Promise.all([funding.reload(), matches.reload(), shares.reload()]); }
  const sections = { market_considerations: "Market considerations", target_customer_analysis: "Target customers", competitor_considerations: "Competitor considerations", indicative_costs: "Indicative costs", suggested_next_steps: "Suggested next steps", assumptions: "Assumptions", sources: "Sources" } as const;
  return <div className="space-y-6"><Section title="Investment funding information"><p className="text-sm text-muted-light">This structured amount is used for matching. Your original planning budget is retained.</p><LoadState {...funding} retry={funding.reload} />{!funding.loading && !funding.error && <ActionForm key={funding.data?.amount ?? "empty"} label="Save funding requirement" fields={[{ name: "amount", label: "Funding required (SAR)", type: "number", value: funding.data?.amount }]} submit={v => api.opportunity(`${path}/funding`, "PUT", { ...v, currency: "SAR" })} done={reload} />}</Section>
    <Section title="Suggested investors"><LoadState {...matches} retry={matches.reload} />{!matches.loading && !matches.data?.length && <p>No compatible investors are currently available. Check the idea's industry and stage or try again later.</p>}{matches.data?.map(m => <div className="space-y-3 border-t border-navy/10 pt-4" key={m.investor_id}><h3 className="font-medium">{m.investor_name}</h3><MatchDetails match={m} />{idea.visibility === "registered" ? <Action run={() => api.opportunity("/contact-requests", "POST", { recipient_id: m.investor_id, idea_id: idea.id })}>Request contact</Action> : <p className="text-sm">Set registered visibility before requesting contact about this idea.</p>}</div>)}</Section>
    <Section title="Approve assessment sharing"><p>Choose a named investor and review the exact assessment below before approving access. New assessments are not automatically shared.</p>
      <LoadState {...versions} retry={versions.reload} />{!!versions.data?.length && <Select label="Assessment version to share" value={selectedVersion || latest?.id || ""} onChange={e => setSelectedVersion(e.target.value)}>{versions.data.map(v => <option key={v.id} value={v.id}>Revision {v.idea_revision} · {new Date(v.created_at).toLocaleString()}</option>)}</Select>}
      {idea.visibility !== "registered" && <Alert kind="info" message="The idea is private. Set registered visibility above before approving a share. Returning to private visibility revokes existing shares." />}
      {assessment ? <><p className="font-medium">Assessment revision {assessment.idea_revision}</p><p className="text-sm">{assessment.provider === "gemini" ? "Generated with Gemini" : assessment.provider === "mock" ? "Simulated demonstration output" : "Provider not recorded"}</p>{assessment.idea_revision !== idea.revision_number && <Alert kind="info" message="This assessment predates the current idea revision." />}<details className="rounded-xl border border-navy/15 p-4" open><summary className="cursor-pointer font-medium">Preview the assessment the investor will receive</summary><div className="mt-4 space-y-5">{Object.entries(sections).map(([key, title]) => <div key={key}><h3 className="font-medium">{title}</h3><p className="mt-1 whitespace-pre-wrap text-sm">{assessment[key as keyof typeof sections] || "Not provided"}</p></div>)}</div></details>
        <LoadState {...investors} retry={investors.reload} />{idea.visibility === "registered" && !!investors.data?.length && <ActionForm label="Approve this assessment for the selected investor" fields={[{ name: "investor_id", label: "Investor", options: [{ value: "", label: "Choose an investor" }, ...investors.data.map(i => ({ value: i.id, label: i.name }))] }]} submit={async v => {
          if (!confirm("I have reviewed this assessment and approve sharing this specific version with the selected investor.")) throw new Error("Sharing was not approved.");
          return api.opportunity(`${path}/assessment-shares`, "POST", { ...v, assessment_id: assessment.id, approved: true });
        }} done={shares.reload} />}{!investors.loading && !investors.data?.length && <p>No participating investors are available yet.</p>}
      </> : <p>Generate a successful assessment before sharing it.</p>}
      <LoadState {...shares} retry={shares.reload} />{shares.data?.map(s => <div className="flex flex-wrap items-center justify-between gap-3 border-t border-navy/10 pt-4" key={s.id}><p>{s.investor_name} · {s.revoked_at ? "Revoked" : "Active"} · {s.assessment_id === assessment?.id ? "Selected assessment version" : "Another assessment version"}</p>{!s.revoked_at && <Action danger run={async () => { await api.opportunity(`/assessment-shares/${s.id}`, "DELETE"); await shares.reload(); }}>Revoke access</Action>}</div>)}
    </Section>
  </div>;
}
