"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { Button } from "@/components/Button";
import { ErrorState, Spinner } from "@/components/States";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ROLE_LABELS, STAGE_LABELS, type Dashboard } from "@/lib/types";

const STATUS_BADGE: Record<string, string> = {
  none: "bg-gray-100 text-gray-600",
  in_progress: "bg-yellow-100 text-yellow-700",
  succeeded: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

export default function DashboardPage() {
  const { user } = useAuth();
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setDashboard(await api.dashboard());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load the dashboard.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) return <Spinner label="Loading your dashboard…" />;
  if (error || !dashboard)
    return <ErrorState message={error ?? "Could not load the dashboard."} onRetry={load} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Welcome, {dashboard.display_name}</h1>
          <p className="text-sm text-gray-500">
            Role: {ROLE_LABELS[dashboard.role]}
          </p>
        </div>
        {dashboard.role === "business_owner" && (
          <Link href="/ideas/new">
            <Button>New business idea</Button>
          </Link>
        )}
      </div>

      {/* Business owner: ideas + assessment status */}
      {dashboard.role === "business_owner" && (
        <section>
          <h2 className="mb-3 text-lg font-semibold text-gray-800">Your business ideas</h2>
          {dashboard.ideas && dashboard.ideas.length > 0 ? (
            <ul className="space-y-3">
              {dashboard.ideas.map((idea) => {
                const badge = STATUS_BADGE[idea.assessment_status] ?? STATUS_BADGE.none;
                const statusText =
                  idea.assessment_status === "none"
                    ? "No assessment"
                    : idea.assessment_status === "in_progress"
                    ? "Generating…"
                    : idea.assessment_status === "succeeded"
                    ? "Assessment ready"
                    : "Last attempt failed";
                return (
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
                        {STAGE_LABELS[idea.business_stage as keyof typeof STAGE_LABELS] ??
                          idea.business_stage}{" "}
                        · Revision {idea.revision_number}
                      </p>
                    </div>
                    <span className={`rounded-full px-3 py-1 text-xs font-medium ${badge}`}>
                      {statusText}
                    </span>
                  </li>
                );
              })}
            </ul>
          ) : (
            <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
              <p className="font-medium text-gray-700">No business ideas yet</p>
              <p className="mt-1 text-sm text-gray-500">
                Create your first idea and get an AI-assessed business analysis.
              </p>
              <Link href="/ideas/new" className="mt-4 inline-block">
                <Button>Create your first idea</Button>
              </Link>
            </div>
          )}
        </section>
      )}

      {/* Innovator / investor: placeholder for later sprints */}
      {(dashboard.role === "innovator" || dashboard.role === "investor") && (
        <section className="rounded-lg border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-800">Coming up</h2>
          <p className="mt-2 text-sm text-gray-600">{dashboard.message}</p>
        </section>
      )}

      {/* Administrator */}
      {dashboard.role === "admin" && (
        <section>
          <h2 className="mb-3 text-lg font-semibold text-gray-800">Administration</h2>
          <ul className="grid gap-3 sm:grid-cols-2">
            {dashboard.admin_actions?.map((action) => (
              <li
                key={action}
                className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-700"
              >
                {action}
                <span className="mt-1 block text-xs text-gray-400">
                  Available in a later sprint
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
