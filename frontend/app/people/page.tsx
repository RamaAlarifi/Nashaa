"use client";
import { useState } from "react";
import Link from "next/link";
import { IndustrySelect } from "@/components/IndustrySelect";
import { Input, Select } from "@/components/Input";
import { Button } from "@/components/Button";
import { LoadState, Section, useResource } from "@/components/OpportunityUI";
import { IndustryLabel } from "@/lib/industries";
import { ROLE_LABELS, type Role } from "@/lib/types";
interface Person { user_id: string; display_name: string; role: Role; location: string; short_description: string; industries: string[] }
export default function PeoplePage() {
  const [filters, setFilters] = useState({ industry: "", role: "", q: "" }), [query, setQuery] = useState("");
  const resource = useResource<Person[]>(`/profiles?${query}`);
  return <div className="space-y-6"><h1 className="text-3xl font-semibold">Discover people</h1><p className="text-muted-light">Find visible business-owner and investor profiles by industry. Innovators can also be found by name and role; they do not have an industry classification.</p>
    <form className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4" onSubmit={e => { e.preventDefault(); setQuery(new URLSearchParams(Object.entries(filters).filter(([, value]) => value)).toString()); }}>
      <Input label="Name or description" value={filters.q} onChange={e => setFilters({ ...filters, q: e.target.value })} />
      <IndustrySelect label="Industry" value={filters.industry} onChange={e => setFilters({ ...filters, industry: e.target.value })} />
      <Select label="Account role" value={filters.role} onChange={e => setFilters({ ...filters, role: e.target.value })}><option value="">All participant roles</option>{(["business_owner", "investor", "innovator"] as const).map(role => <option key={role} value={role}>{ROLE_LABELS[role]}</option>)}</Select>
      <Button type="submit">Filter profiles</Button>
    </form><LoadState {...resource} retry={resource.reload} />
    {!resource.loading && !resource.error && !resource.data?.length && <Section title="No matching profiles"><p>Try another category or role. Private and inactive profiles are excluded.</p></Section>}
    <div className="grid gap-5 md:grid-cols-2">{resource.data?.map(p => <Section key={p.user_id} title={p.display_name}><p>{ROLE_LABELS[p.role]} · {p.location || "Location not provided"}</p><p className="whitespace-pre-wrap">{p.short_description}</p><p>{p.industries.length ? p.industries.map((value, index) => <span key={value}>{index > 0 && " · "}<IndustryLabel value={value} /></span>) : "Industry not selected"}</p><Link href={`/people/${p.user_id}`} className="text-brand-700 underline">View profile</Link></Section>)}</div>
  </div>;
}
