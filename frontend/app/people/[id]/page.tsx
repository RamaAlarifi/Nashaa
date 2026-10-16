"use client";
import { useParams } from "next/navigation";
import { LoadState, Section, useResource } from "@/components/OpportunityUI";
import { IndustryLabel } from "@/lib/industries";
import type { Profile } from "@/lib/types";
export default function PersonPage() {
  const { id } = useParams<{ id: string }>(); const resource = useResource<Profile>(`/users/${id}/profile`); const p = resource.data;
  return <div className="space-y-6"><h1 className="text-3xl font-semibold">Participant profile</h1><LoadState {...resource} retry={resource.reload} />{p && <Section title={p.display_name}><p>{p.location || "Location not provided"}</p><p className="whitespace-pre-wrap">{p.short_description || "No description provided."}</p>{Object.entries(p.role_specific_info).map(([key, value]) => <div key={key}><h2 className="text-sm font-medium capitalize">{key.replaceAll("_", " ")}</h2><p className="whitespace-pre-wrap">{key === "industry" ? <IndustryLabel value={String(value)} /> : String(value || "Not provided")}</p></div>)}</Section>}</div>;
}
