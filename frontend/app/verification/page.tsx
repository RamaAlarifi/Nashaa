"use client";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ActionForm, LoadState, Section, useResource } from "@/components/OpportunityUI";
import type { Verification } from "@/lib/opportunity-types";

export default function VerificationPage() {
  const { user, refresh } = useAuth(); const admin = user?.role === "admin";
  const own = useResource<{ status: string; requests: Verification[] }>(!admin && user ? "/verification" : null);
  const queue = useResource<Verification[]>(admin ? "/admin/verification" : null);
  async function reload() { await Promise.all([own.reload(), queue.reload(), refresh()]); }
  return <div className="space-y-6"><h1 className="text-3xl font-semibold">{admin ? "Verification review" : "Account verification"}</h1>
    <p className="text-muted-light">Nashaa verification is platform approval, not official government identity verification. Do not submit identity documents or sensitive identifiers.</p>
    <LoadState {...(admin ? queue : own)} retry={reload} />
    {!admin && own.data && <><Section title={`Current status: ${own.data.status}`}><p>Approved verification is required for proposals and messaging.</p></Section>
      {!["approved", "pending"].includes(own.data.status) && <Section title="Request verification"><ActionForm label="Submit verification request" fields={[
        { name: "information", label: "Professional or business information", type: "textarea", maxLength: 4000, hint: "Provide at least 20 characters explaining your role and relevant background." },
        { name: "reference", label: "Optional public reference", required: false, maxLength: 500 },
      ]} submit={v => api.opportunity("/verification", "POST", v)} done={reload} /></Section>}
      {own.data.requests.map(r => <Section key={r.id} title={`Request: ${r.status}`}><p className="whitespace-pre-wrap">{r.information}</p>{r.reference && <p>{r.reference}</p>}<p>Decision: {r.decision_reason || "Awaiting review"}</p></Section>)}</>}
    {admin && !queue.loading && !queue.error && !queue.data?.length && <Section title="No verification requests"><p>Submitted requests will appear here.</p></Section>}
    {admin && queue.data?.map(r => <Section key={r.id} title={`${r.applicant_name} · ${r.status}`}><p className="whitespace-pre-wrap">{r.information}</p><p>{r.reference}</p>{r.status === "pending" ? <ActionForm label="Record decision" fields={[
      { name: "decision", label: "Decision", options: [{ value: "approved", label: "Approve" }, { value: "rejected", label: "Reject" }] }, { name: "reason", label: "Decision reason", type: "textarea", maxLength: 2000 },
    ]} submit={v => api.opportunity(`/admin/verification/${r.id}/decision`, "POST", v)} done={reload} /> : <p>{r.decision_reason}</p>}</Section>)}
  </div>;
}
