"use client";
import Link from "next/link";
import { LoadState, Section, useResource } from "@/components/OpportunityUI";
import type { Proposal } from "@/lib/opportunity-types";
export default function ProposalsPage() {
  const r = useResource<Proposal[]>("/proposals");
  return <div className="space-y-6"><h1 className="text-3xl font-semibold">My proposals</h1><LoadState {...r} retry={r.reload} />{!r.loading && !r.error && !r.data?.length && <Section title="No proposals yet"><Link className="text-brand-700 underline" href="/challenges">Discover challenges</Link></Section>}{r.data?.map(p => <Section key={p.id} title={p.challenge_title ?? "Challenge proposal"}><p>Status: {p.status.replaceAll("_", " ")}</p><p className="whitespace-pre-wrap">{p.approach}</p><p>{p.timeline}</p><Link className="text-brand-700 underline" href={`/challenges/${p.challenge_id}`}>Open challenge</Link></Section>)}</div>;
}
