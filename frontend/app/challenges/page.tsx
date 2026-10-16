"use client";
import { useState } from "react";
import { IndustrySelect } from "@/components/IndustrySelect";
import { IndustryLabel } from "@/lib/industries";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Input } from "@/components/Input";
import { Button, ButtonLink } from "@/components/Button";
import { Section, LoadState, useResource } from "@/components/OpportunityUI";
import type { Challenge } from "@/lib/opportunity-types";

export default function ChallengesPage() {
  const { user } = useAuth(); const owner = user?.role === "business_owner";
  const [filters, setFilters] = useState({ q: "", industry: "", location: "", skill: "" });
  const [query, setQuery] = useState("");
  const resource = useResource<Challenge[]>(user ? `/challenges?mine=${owner}&${query}` : null);
  return <div className="space-y-6"><div className="flex flex-wrap items-center justify-between gap-4"><h1 className="text-3xl font-semibold">{owner ? "My challenges" : "Discover challenges"}</h1>{owner && <ButtonLink href="/challenges/new">Create challenge</ButtonLink>}</div>
    <p className="text-muted-light">{owner ? "Review and approve a draft before making it available to innovators." : "Find published opportunities that fit your skills."}</p>
    <form className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5" onSubmit={e => { e.preventDefault(); setQuery(new URLSearchParams(filters).toString()); }}>
      {Object.entries(filters).map(([key, value]) => key === "industry" ? <IndustrySelect key={key} label="Industry" value={value} onChange={e => setFilters({ ...filters, industry: e.target.value })} /> : <Input key={key} label={key === "q" ? "Search" : key[0].toUpperCase() + key.slice(1)} value={value} onChange={e => setFilters({ ...filters, [key]: e.target.value })} />)}<Button type="submit">Apply filters</Button>
    </form><LoadState {...resource} retry={resource.reload} />
    {!resource.loading && !resource.error && !resource.data?.length && <Section title="No challenges found"><p>Try different filters{owner ? " or create your first draft" : " or check again later"}.</p></Section>}
    <div className="grid gap-5 md:grid-cols-2">{resource.data?.map(c => <Section key={c.id} title={c.title}><p className="text-sm font-medium capitalize">{c.status} · <IndustryLabel value={c.industry} /> · {c.location}</p><p className="whitespace-pre-wrap">{c.desired_outcome}</p><p className="text-sm">Skills: {c.required_skills.join(", ")}</p><Link className="text-brand-700 underline" href={`/challenges/${c.id}`}>Open challenge</Link></Section>)}</div>
  </div>;
}
