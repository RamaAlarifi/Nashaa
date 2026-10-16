"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Action, ActionForm, LoadState, Section, useResource } from "@/components/OpportunityUI";
import { Button } from "@/components/Button";
import type { Contact, Conversation, Message } from "@/lib/opportunity-types";

export default function MessagesPage() {
  const { user } = useAuth(); const [selected, setSelected] = useState<string | null>(null);
  const pref = useResource<{ preference: string }>("/contact-preference");
  const contacts = useResource<Contact[]>("/contact-requests");
  const threads = useResource<Conversation[]>("/conversations");
  const messages = useResource<Message[]>(selected ? `/conversations/${selected}/messages` : null);
  async function reload() { await Promise.all([contacts.reload(), threads.reload(), pref.reload(), messages.reload()]); }
  useEffect(() => { if (!selected) return; const timer = window.setInterval(messages.reload, 5000); return () => clearInterval(timer); }, [selected, messages.reload]);
  return <div className="space-y-6"><h1 className="text-3xl font-semibold">Messages and contact permissions</h1><p className="text-muted-light">Both participants need approved verification. Start contact from a relevant challenge or investment opportunity.</p>
    <Section title="Contact preference"><LoadState {...pref} retry={pref.reload} />{pref.data && <ActionForm key={pref.data.preference} label="Save contact preference" fields={[{ name: "preference", label: "Who may contact me", value: pref.data.preference, options: [{ value: "contact_request", label: "Ask for my approval" }, { value: "open", label: "Eligible participants may open contact" }, { value: "closed", label: "Contact closed" }] }]} submit={v => api.opportunity("/contact-preference", "PUT", v)} done={reload} />}<p className="text-sm text-muted-light">Closed contact or revoked permission blocks sending and reading conversation messages until eligibility and permission are restored.</p></Section>
    <Section title="Contact requests"><LoadState {...contacts} retry={contacts.reload} />{!contacts.loading && !contacts.data?.length && <p>No contact requests yet.</p>}{contacts.data?.map(r => <div className="space-y-3 border-t border-navy/10 pt-4" key={r.id}><p>{r.recipient_id === user?.id ? "Incoming" : "Outgoing"} · {r.status} · {r.participant_name} · {r.context_title}</p><div className="flex flex-wrap gap-3">{r.status === "pending" && r.recipient_id === user?.id && ["accepted", "rejected"].map(decision => <Action key={decision} run={async () => { await api.opportunity(`/contact-requests/${r.id}/decision`, "POST", { decision }); await reload(); }}>{decision === "accepted" ? "Accept" : "Reject"}</Action>)}{["accepted", "pending"].includes(r.status) && <Action danger run={async () => { await api.opportunity(`/contact-requests/${r.id}/decision`, "POST", { decision: "revoked" }); await reload(); }}>Revoke permission</Action>}</div></div>)}</Section>
    <div className="grid gap-6 lg:grid-cols-[1fr_2fr]"><Section title="Conversations"><LoadState {...threads} retry={threads.reload} />{!threads.loading && !threads.data?.length && <p>Accepted contact requests open a conversation here.</p>}{threads.data?.map(t => <Button className="w-full justify-start text-left" variant={t.id === selected ? "primary" : "secondary"} key={t.id} onClick={() => setSelected(t.id)}>{t.participant_name} · {t.context_title}</Button>)}</Section>
      <Section title="Conversation messages">{selected ? <><LoadState {...messages} retry={messages.reload} /><div className="max-h-[32rem] space-y-4 overflow-y-auto" aria-live="polite">{messages.data?.map(m => <div className={`rounded-xl p-4 ${m.sender_id === user?.id ? "bg-brand-50" : "bg-sand-100"}`} key={m.id}><p className="text-xs text-muted-light">{m.sender_id === user?.id ? "You" : "Participant"} · {new Date(m.created_at).toLocaleString()}</p><p className="mt-2 whitespace-pre-wrap break-words">{m.body}</p></div>)}{!messages.loading && !messages.error && !messages.data?.length && <p>No messages yet.</p>}</div>{!messages.error && <ActionForm resetOnSuccess label="Send message" fields={[{ name: "body", label: "Message", type: "textarea", maxLength: 4000 }]} submit={v => api.opportunity(`/conversations/${selected}/messages`, "POST", v)} done={messages.reload} />}</> : <p>Choose a conversation to view its messages.</p>}</Section>
    </div>
  </div>;
}
