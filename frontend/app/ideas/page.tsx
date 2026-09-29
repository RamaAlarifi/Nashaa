"use client";

import { useEffect, useState } from "react";
import { Button, ButtonLink } from "@/components/Button";
import { Icon } from "@/components/Icon";
import { IdeaCard } from "@/components/IdeaCard";
import { Input, Select } from "@/components/Input";
import { EmptyState, ErrorState, Spinner } from "@/components/States";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { STAGE_LABELS, type BusinessIdea } from "@/lib/types";

export default function IdeasPage() {
  const { user } = useAuth();
  const [ideas, setIdeas] = useState<BusinessIdea[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [stage, setStage] = useState("");
  async function load() {
    setLoading(true);
    setError(null);
    try {
      setIdeas(await api.listIdeas());
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not load your ideas.",
      );
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    load();
  }, []);
  if (loading) return <Spinner label="Loading your ideas…" />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  const filtered = ideas.filter(
    (idea) =>
      (!stage || idea.business_stage === stage) &&
      `${idea.name} ${idea.industry}`
        .toLowerCase()
        .includes(query.trim().toLowerCase()),
  );
  return (
    <div className="space-y-8">
      <div className="page-heading">
        <div>
          <p className="eyebrow text-brand-700">Room to grow</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight lg:text-4xl">
            Your business ideas
          </h1>
          <p className="mt-3 text-sm text-muted-light">
            From the first spark to your next step. Keep it all here.
          </p>
        </div>
        {user?.role === "business_owner" && (
          <ButtonLink href="/ideas/new">
            <Icon name="plus" className="h-4 w-4" />
            New idea
          </ButtonLink>
        )}
      </div>
      {ideas.length > 0 && (
        <div className="grid items-end gap-4 rounded-2xl border border-navy/10 bg-white p-5 sm:grid-cols-[1fr_220px]">
          <Input
            label="Search ideas"
            type="search"
            name="search"
            placeholder="Search by name or industry"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <Select
            label="Business stage"
            name="stage-filter"
            value={stage}
            onChange={(e) => setStage(e.target.value)}
          >
            <option value="">All stages</option>
            {Object.entries(STAGE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </Select>
        </div>
      )}
      {ideas.length === 0 ? (
        <EmptyState
          title="Make room for your next big idea"
          description={
            user?.role === "business_owner"
              ? "Capture a problem worth solving. You can refine the details as you go."
              : "Business ideas you own will appear here. Idea creation is available to business owners."
          }
          action={
            user?.role === "business_owner" ? (
              <ButtonLink href="/ideas/new">Create your first idea</ButtonLink>
            ) : undefined
          }
        />
      ) : (
        <section>
          <p className="mb-4 text-xs text-muted-light" role="status">
            {filtered.length} {filtered.length === 1 ? "idea" : "ideas"}
            {query || stage ? " matching your filters" : " in your workspace"}
          </p>
          {filtered.length ? (
            <ul className="space-y-3">
              {filtered.map((idea) => (
                <li key={idea.id}>
                  <IdeaCard idea={idea} />
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              title="No matching ideas"
              description="Try a different name, industry, or business stage."
              action={
                <Button
                  variant="secondary"
                  onClick={() => {
                    setQuery("");
                    setStage("");
                  }}
                >
                  Clear filters
                </Button>
              }
            />
          )}
        </section>
      )}
    </div>
  );
}
