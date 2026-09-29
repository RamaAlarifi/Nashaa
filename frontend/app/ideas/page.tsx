"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { Button } from "@/components/Button";
import { EmptyState, ErrorState, Spinner } from "@/components/States";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { STAGE_LABELS, VISIBILITY_LABELS, type BusinessIdea } from "@/lib/types";

export default function IdeasPage() {
  const { user } = useAuth();
  const [ideas, setIdeas] = useState<BusinessIdea[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setIdeas(await api.listIdeas());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load your ideas.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) return <Spinner label="Loading your ideas…" />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Business ideas</h1>
          <p className="text-sm text-gray-500">Create, edit, and assess your ideas.</p>
        </div>
        {user?.role === "business_owner" && (
          <Link href="/ideas/new">
            <Button>New idea</Button>
          </Link>
        )}
      </div>

      {ideas.length === 0 ? (
        <EmptyState
          title="No business ideas yet"
          description="Create your first idea to get an AI-assessed business analysis."
          action={
            user?.role === "business_owner" ? (
              <Link href="/ideas/new">
                <Button>Create your first idea</Button>
              </Link>
            ) : undefined
          }
        />
      ) : (
        <ul className="space-y-3">
          {ideas.map((idea) => (
            <li
              key={idea.id}
              className="flex flex-col gap-2 rounded-lg border border-gray-200 bg-white p-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <Link
                  href={`/ideas/${idea.id}`}
                  className="font-medium text-brand-700 hover:underline"
                >
                  {idea.name}
                </Link>
                <p className="text-sm text-gray-500">
                  {idea.industry || "No industry"} ·{" "}
                  {STAGE_LABELS[idea.business_stage]} · Revision {idea.revision_number}
                </p>
              </div>
              <span className="text-xs text-gray-400">
                {VISIBILITY_LABELS[idea.visibility]}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
