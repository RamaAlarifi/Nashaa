"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ButtonLink } from "@/components/Button";
import { Card } from "@/components/Card";
import { Icon } from "@/components/Icon";
import { IdeaCard } from "@/components/IdeaCard";
import { EmptyState, ErrorState, Spinner } from "@/components/States";
import { ApiError, api } from "@/lib/api";
import { ROLE_LABELS, type Dashboard } from "@/lib/types";

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  async function load() {
    setLoading(true);
    setError(null);
    try {
      setDashboard(await api.dashboard());
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not load the dashboard.",
      );
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    load();
  }, []);
  if (loading) return <Spinner label="Loading your dashboard…" />;
  if (error || !dashboard)
    return (
      <ErrorState
        message={error ?? "Could not load the dashboard."}
        onRetry={load}
      />
    );
  const ideas = dashboard.ideas ?? [];
  const owner = dashboard.role === "business_owner";
  const assessed = ideas.filter(
    (idea) => idea.assessment_status === "succeeded",
  ).length;
  return (
    <div className="space-y-8">
      <div className="page-heading">
        <div className="min-w-0">
          <p className="eyebrow text-brand-700">
            {ROLE_LABELS[dashboard.role]} workspace
          </p>
          <h1 className="mt-2 break-words text-3xl font-semibold tracking-tight lg:text-4xl">
            Welcome back, {dashboard.display_name}.
          </h1>
          <p className="mt-3 text-sm text-muted-light">
            A little clarity today. A stronger business tomorrow.
          </p>
        </div>
        {owner && (
          <ButtonLink href="/ideas/new">
            <Icon name="plus" className="h-4 w-4" />
            New business idea
          </ButtonLink>
        )}
      </div>
      {owner && (
        <>
          <section className="dashboard-hero">
            <div className="relative z-10 max-w-lg">
              <p className="eyebrow text-turquoise-400">Your next move</p>
              <h2 className="mt-4 text-3xl font-medium leading-tight tracking-tight text-white sm:text-4xl">
                Turn a possibility
                <br />
                into a plan.
              </h2>
              <p className="mt-4 max-w-sm text-sm leading-relaxed text-navy-100">
                Capture what you have in mind. Explore your market, customers,
                and next steps with an AI business assessment.
              </p>
              <ButtonLink
                href={ideas.length ? `/ideas/${ideas[0].id}` : "/ideas/new"}
                className="mt-6 !bg-white !text-navy hover:!bg-brand-50"
              >
                {ideas.length ? "Continue your idea" : "Start your first idea"}
                <Icon name="arrow" className="h-4 w-4" />
              </ButtonLink>
            </div>
            <div className="orbit-art" aria-hidden="true">
              <div className="orbit-ring orbit-ring-outer" />
              <div className="orbit-ring orbit-ring-inner" />
              <span className="orbit-core">
                <Icon name="idea" className="h-12 w-12" />
              </span>
              <span className="orbit-label orbit-label-top">
                <Icon name="spark" className="h-4 w-4" />
                Find clarity
              </span>
              <span className="orbit-label orbit-label-bottom">
                <Icon name="check" className="h-4 w-4" />
                Build with purpose
              </span>
            </div>
          </section>
          <section
            aria-label="Your idea activity"
            className="grid gap-4 sm:grid-cols-3"
          >
            {[
              {
                label: "Ideas in your workspace",
                value: ideas.length,
                icon: "idea",
              },
              {
                label: "Latest assessments ready",
                value: assessed,
                icon: "spark",
              },
              {
                label: "Ideas kept private",
                value: ideas.filter((idea) => idea.visibility === "private")
                  .length,
                icon: "lock",
              },
            ].map((stat) => (
              <Card key={stat.label} className="flex items-center gap-4 p-5">
                <span className="rounded-xl bg-sand p-3 text-brand-700">
                  <Icon name={stat.icon as "idea" | "spark" | "lock"} />
                </span>
                <div>
                  <p className="text-2xl font-semibold tabular-nums">
                    {stat.value.toString().padStart(2, "0")}
                  </p>
                  <p className="mt-1 text-xs text-muted-light">{stat.label}</p>
                </div>
              </Card>
            ))}
          </section>
          <section>
            <div className="mb-5 flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold tracking-tight">
                  Your business ideas
                </h2>
                <p className="mt-1 text-sm text-muted-light">
                  Pick up where you left off.
                </p>
              </div>
              <Link
                href="/ideas"
                className="flex shrink-0 items-center gap-2 text-sm font-medium text-brand-700 hover:underline"
              >
                View all
                <Icon name="arrow" className="h-4 w-4" />
              </Link>
            </div>
            {ideas.length ? (
              <ul className="space-y-3">
                {ideas.slice(0, 4).map((idea) => (
                  <li key={idea.id}>
                    <IdeaCard idea={idea} />
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState
                title="Every business starts with an idea"
                description="You don't need all the answers. Start with the problem you want to solve."
                action={
                  <ButtonLink href="/ideas/new">
                    Create your first idea
                    <Icon name="arrow" className="h-4 w-4" />
                  </ButtonLink>
                }
              />
            )}
          </section>
        </>
      )}
      {!owner && (
        <Card className="p-8">
          <Icon name="user" className="mb-5 h-8 w-8 text-brand-700" />
          <h2 className="text-2xl font-semibold">Your account workspace</h2>
          <p className="mt-3 text-sm text-muted-light">{dashboard.message}</p>
          <ButtonLink href="/profile" variant="secondary" className="mt-6">
            Edit your profile <Icon name="arrow" className="h-4 w-4" />
          </ButtonLink>
        </Card>
      )}
    </div>
  );
}
