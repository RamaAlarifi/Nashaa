"use client";
import { useState } from "react";
import { IndustryLabel } from "@/lib/industries";
import Link from "next/link";
import { api } from "@/lib/api";
import { Action, ActionForm, LoadState, MatchDetails, Section, splitList, stageOptions, useResource } from "@/components/OpportunityUI";
import { Button } from "@/components/Button";
import type { History, Match, Preference, SharedAssessment } from "@/lib/opportunity-types";

export default function InvestmentsPage() {
  const pref = useResource<Preference>("/investor-preferences"); const history = useResource<History[]>("/investment-history");
  const feed = useResource<Match[]>("/investor/projects"); const shares = useResource<SharedAssessment[]>("/assessment-shares");
  const [editing, setEditing] = useState<History | null>(null);
  async function reload() { await Promise.all([pref.reload(), history.reload(), feed.reload(), shares.reload()]); }
  return <div className="space-y-6"><h1 className="text-3xl font-semibold">Investment workspace</h1><p className="text-muted-light">Keep your preferences current and review explained project suggestions. History is optional.</p>
    <Section title="Investment preferences"><LoadState {...pref} retry={pref.reload} />{!pref.loading && !pref.error && <ActionForm key={JSON.stringify(pref.data)} label="Save preferences" fields={[
      { name: "industries", label: "Industries", type: "industries", value: pref.data?.industries.join(", ") },
      { name: "stages", label: "Business stages", value: pref.data?.stages.join(", "), hint: "Use idea, validation, early, operating or scaling, separated with commas." },
      { name: "locations", label: "Preferred locations", value: pref.data?.locations.join(", "), required: false, hint: "Leave empty for any location." },
      { name: "min_funding", label: "Minimum investment (SAR)", type: "number", value: pref.data?.min_funding ?? "0" }, { name: "max_funding", label: "Maximum investment (SAR)", type: "number", value: pref.data?.max_funding ?? "0" },
    ]} submit={v => api.opportunity("/investor-preferences", "PUT", { ...v, industries: splitList(v.industries), stages: splitList(v.stages).map(s => s.toLowerCase()), locations: splitList(v.locations) })} done={reload} />}</Section>
    <Section title="Investment history"><LoadState {...history} retry={history.reload} /><p className="text-sm">Record permitted, relevant history and its source. Clearly label fictional demonstration entries.</p>
      <ActionForm key={editing?.id ?? "new"} label={editing ? "Save history changes" : "Add history entry"} fields={[
        { name: "project_name", label: "Project name", value: editing?.project_name }, { name: "industry", label: "Industry", type: "industry", value: editing?.industry }, { name: "stage", label: "Stage", value: editing?.stage, options: stageOptions }, { name: "source", label: "Source or provenance", value: editing?.source, maxLength: 500 },
      ]} submit={async v => { await api.opportunity(editing ? `/investment-history/${editing.id}` : "/investment-history", editing ? "PUT" : "POST", v); setEditing(null); }} done={reload} />
      {editing && <Button variant="ghost" onClick={() => setEditing(null)}>Cancel editing</Button>}
      {!history.loading && !history.data?.length && <p>No history recorded. Matching will use your current preferences.</p>}
      {history.data?.map(h => <div className="space-y-2 border-t border-navy/10 pt-4" key={h.id}><p className="font-medium">{h.project_name} · <IndustryLabel value={h.industry} /> · {h.stage}</p><p>Source: {h.source}</p><div className="flex gap-3"><Button variant="secondary" onClick={() => setEditing(h)}>Edit</Button><Action danger run={async () => { if (confirm("Remove this investment history entry?")) { await api.opportunity(`/investment-history/${h.id}`, "DELETE"); await reload(); } }}>Remove</Action></div></div>)}
    </Section>
    <Section title="Ranked projects"><LoadState {...feed} retry={feed.reload} />{!feed.loading && !feed.data?.length && <p>No compatible registered projects. Save your preferences or check again later.</p>}{feed.data?.map(m => <div key={m.idea.id} className="space-y-4 border-t border-navy/10 pt-5"><h3 className="font-semibold">{m.idea.name}</h3><p><IndustryLabel value={m.idea.industry} /> · {m.idea.business_stage} · {m.idea.target_location}</p><MatchDetails match={m} /><div className="flex flex-wrap items-center gap-4"><Link className="text-brand-700 underline" href={`/ideas/${m.idea.id}`}>View shared idea summary</Link><Action run={() => api.opportunity("/contact-requests", "POST", { recipient_id: m.idea.owner_id, idea_id: m.idea.id })}>Request contact</Action></div><p className="text-sm text-muted-light">Assessments require separate approval from the owner.</p></div>)}</Section>
    <Section title="Assessments shared with you"><LoadState {...shares} retry={shares.reload} />{!shares.loading && !shares.data?.length && <p>No assessments have been explicitly shared with you.</p>}{shares.data?.map(s => <div key={s.share_id} className="border-t border-navy/10 py-4"><Link className="font-medium text-brand-700 underline" href={`/shared-assessments/${s.share_id}`}>{s.idea.name} · assessment revision {s.assessment.idea_revision}</Link></div>)}</Section>
  </div>;
}
