"use client";
import Link from "next/link";
import { LoadState,Section,useResource } from "@/components/OpportunityUI";
import type { Collaboration } from "@/lib/completion-types";
export default function CollaborationsPage(){const r=useResource<Collaboration[]>("/collaborations");return <div className="space-y-6"><h1 className="text-3xl font-semibold">Collaborations</h1><p>Record agreed work, share progress and confirm completion.</p><LoadState {...r} retry={r.reload}/>{!r.loading&&!r.error&&!r.data?.length&&<Section title="No collaborations yet"><p>Selected challenge proposals appear here for the business owner and innovator.</p></Section>}{r.data?.map(c=><Section key={c.id} title={c.challenge_title}><p>Status: {c.status}</p><Link href={`/collaborations/${c.id}`} className="text-brand-700 underline">Open collaboration</Link></Section>)}</div>;}
