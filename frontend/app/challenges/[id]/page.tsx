"use client";
import { useParams } from "next/navigation";
import { useState } from "react";
import { IndustryLabel } from "@/lib/industries";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ChallengeEditor } from "@/components/ChallengeEditor";
import { Action, ActionForm, LoadState, Section, useResource } from "@/components/OpportunityUI";
import { Button } from "@/components/Button";
import type { Challenge, Proposal } from "@/lib/opportunity-types";

export default function ChallengePage() {
  const { id } = useParams<{ id: string }>(); const { user } = useAuth(); const [editing, setEditing] = useState(false);
  const resource = useResource<Challenge>(`/challenges/${id}`); const c = resource.data; const owner = c?.owner_id === user?.id;
  const proposals = useResource<Proposal[]>(owner ? `/challenges/${id}/proposals` : null);
  const own = useResource<Proposal[]>(user?.role === "innovator" ? "/proposals" : null);
  const existing = own.data?.find(p => p.challenge_id === id);
  async function reload() { await Promise.all([resource.reload(), proposals.reload(), own.reload()]); }
  return <div className="space-y-6"><LoadState {...resource} retry={resource.reload} />{c && <>
    <h1 className="text-3xl font-semibold">{c.title}</h1><p className="capitalize">{c.status} · <IndustryLabel value={c.industry} /> · {c.location}</p>
    <Section title="The opportunity"><h3 className="font-medium">Problem</h3><p className="whitespace-pre-wrap">{c.problem || "Not provided"}</p><h3 className="font-medium">Desired outcome</h3><p className="whitespace-pre-wrap">{c.desired_outcome || "Not provided"}</p><p>Skills: {c.required_skills.join(", ") || "Not provided"}</p><p>Timeline: {c.timeline || "Not provided"}</p><p>Compensation: {c.compensation || "To be discussed"}</p></Section>
    {owner && <Section title="Manage challenge"><div className="flex flex-wrap gap-3">
      {c.status !== "closed" && <Button variant="secondary" onClick={() => setEditing(!editing)}>{editing ? "Cancel editing" : "Edit draft"}</Button>}
      {c.status === "draft" && <Action run={async () => { if (confirm("I have reviewed this challenge and approve its publication.")) { await api.opportunity(`/challenges/${id}/publish`, "POST", { approved: true }); await reload(); } }}>Approve and publish</Action>}
      {c.status !== "closed" && <Action danger run={async () => { if (confirm("Close this challenge to new proposals?")) { await api.opportunity(`/challenges/${id}/close`, "POST"); await reload(); } }}>Close challenge</Action>}
      </div>{editing && <><p>Saving changes returns the challenge to draft. Challenges with submitted proposals cannot be edited.</p><ChallengeEditor challenge={c} done={async () => { setEditing(false); await reload(); }} /></>}</Section>}
    {owner && <Section title="Compare proposals"><LoadState {...proposals} retry={proposals.reload} />{!proposals.loading && !proposals.data?.length && <p>No proposals have been submitted yet.</p>}
      <div className="overflow-x-auto">{!!proposals.data?.length && <table className="w-full text-left text-sm"><thead><tr>{["Innovator", "Approach", "Deliverables", "Timeline", "Cost (SAR)", "Decision"].map(h => <th className="border-b p-3" key={h}>{h}</th>)}</tr></thead><tbody>{proposals.data.map(p => <tr key={p.id}><td className="p-3">{p.innovator_name}</td><td className="whitespace-pre-wrap p-3">{p.approach}</td><td className="whitespace-pre-wrap p-3">{p.deliverables}</td><td className="p-3">{p.timeline}</td><td className="p-3">{p.cost ?? "Not specified"}</td><td className="space-y-3 p-3"><p>{p.status.replaceAll("_", " ")}</p>{c.status === "published" && <Action run={async () => { if (confirm("Select this innovator? This closes the challenge and records the collaboration.")) { await api.opportunity(`/challenges/${id}/select/${p.id}`, "POST"); await reload(); } }}>Select collaborator</Action>}<Action run={() => api.opportunity("/contact-requests", "POST", { recipient_id: p.innovator_id, challenge_id: id })}>Request contact</Action></td></tr>)}</tbody></table>}</div>
    </Section>}
    {user?.role === "innovator" && <Section title={existing ? "Your proposal" : "Submit a proposal"}>
      {existing ? <><p>Status: {existing.status.replaceAll("_", " ")}</p><p className="whitespace-pre-wrap">{existing.approach}</p><p className="whitespace-pre-wrap">{existing.deliverables}</p><p>{existing.timeline} · {existing.cost ?? "No cost specified"}</p></> : c.status === "published" ? <><p>Approved account verification is required before submission.</p><ActionForm label="Submit proposal" fields={[
        { name: "approach", label: "Proposed approach", type: "textarea" }, { name: "deliverables", label: "Deliverables", type: "textarea" }, { name: "timeline", label: "Expected timeline" }, { name: "cost", label: "Proposed cost (SAR)", type: "number", required: false },
      ]} submit={v => api.opportunity(`/challenges/${id}/proposals`, "POST", { ...v, cost: v.cost || null })} done={reload} /></> : <p>This challenge is closed to new proposals.</p>}
      <Action run={() => api.opportunity("/contact-requests", "POST", { recipient_id: c.owner_id, challenge_id: id })}>Request contact with owner</Action>
    </Section>}
  </>}</div>;
}
