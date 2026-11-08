"use client";
import Link from "next/link";
import { LoadState,Section,useResource } from "@/components/OpportunityUI";
import type { Lead } from "@/lib/completion-types";
export default function LeadsPage(){const r=useResource<Lead[]>("/leads");return <div className="space-y-6"><h1 className="text-3xl font-semibold">Saved leads</h1><LoadState {...r} retry={r.reload}/>{!r.loading&&!r.error&&!r.data?.length&&<Section title="No saved leads"><p>Save customers from an idea&apos;s customer discovery page, or investors from its suggested investors.</p><Link href="/ideas" className="text-brand-700 underline">Open my ideas</Link></Section>}{r.data?.map(lead=><Section key={lead.id} title={String(lead.snapshot.name)}><p>{lead.kind} · {lead.idea_name} · {lead.status.replaceAll("_"," ")}</p><p>Source: {lead.snapshot.source}</p><Link href={`/leads/${lead.id}`} className="text-brand-700 underline">Open lead</Link></Section>)}</div>;}
