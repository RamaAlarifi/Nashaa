"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ButtonLink } from "@/components/Button";
import { Card } from "@/components/Card";
import { Icon, type IconName } from "@/components/Icon";
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
  const role = dashboard.role;
  const allActions: { href: string; label: string; note: string; icon: IconName; show: boolean }[] = [
    { href: "/collaborations", label: "Collaborations", note: "Work with your partners", icon: "link", show: owner || role === "innovator" },
    { href: "/leads", label: "Saved leads", note: "People you want to follow up", icon: "bookmark", show: owner },
    { href: "/admin", label: "Platform administration", note: "Moderation and platform tools", icon: "lock", show: role === "admin" },
    { href: "/challenges", label: owner ? "Manage challenges" : "Discover challenges", note: owner ? "Publish and review challenges" : "Find problems worth solving", icon: "target", show: owner || role === "innovator" },
    { href: "/proposals", label: "My proposals", note: "Track what you have submitted", icon: "file", show: role === "innovator" },
    { href: "/investments", label: "Investment workspace", note: "Opportunities you are following", icon: "trend", show: role === "investor" },
    { href: "/verification", label: role === "admin" ? "Review verification" : "Account verification", note: role === "admin" ? "Pending verification requests" : "Build trust with your profile", icon: "shield", show: true },
    { href: "/messages", label: "Messages", note: "Your conversations", icon: "chat", show: role !== "admin" },
  ];
  const quickActions = allActions.filter((action) => action.show);
  return (
    <div className="space-y-10">
      <div className="page-heading">
        <div className="min-w-0">
          <p className="eyebrow text-brand-700">
            {ROLE_LABELS[dashboard.role]} workspace
          </p>
          <h1 className="mt-3 break-words text-3xl font-semibold tracking-tight lg:text-[2.5rem] lg:leading-[1.1]">
            Welcome back, {dashboard.display_name}.
          </h1>
          <p className="mt-3 text-[0.9375rem] text-muted-light">
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
      <section aria-label="Quick actions">
        <h2 className="sr-only">Quick actions</h2>
        <ul className="stagger grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {quickActions.map((action) => (
            <li key={action.href}>
              <Link href={action.href} className="action-tile group h-full">
                <span className="icon-chip">
                  <Icon name={action.icon} />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block text-sm font-semibold text-navy transition-colors group-hover:text-brand-700">
                    {action.label}
                  </span>
                  <span className="mt-0.5 block truncate text-xs text-muted-light">
                    {action.note}
                  </span>
                </span>
                <Icon
                  name="arrow"
                  className="h-4 w-4 shrink-0 text-navy/25 transition-all duration-200 group-hover:translate-x-0.5 group-hover:text-brand-600"
                />
              </Link>
            </li>
          ))}
        </ul>
      </section>
      {owner && (
        <>
          <section className="dashboard-hero">
            <div className="relative z-10 max-w-lg">
              <p className="eyebrow text-turquoise-400">Your next move</p>
              <h2 className="mt-4 text-3xl font-medium leading-[1.1] tracking-tight text-white sm:text-[2.75rem]">
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
                size="lg"
                className="mt-8 !bg-white !text-navy !shadow-[0_8px_24px_-8px_#00000066] hover:!bg-brand-50"
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
            className="stagger grid gap-4 sm:grid-cols-3"
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
              <div key={stat.label} className="stat-tile">
                <div className="flex items-start justify-between gap-4">
                  <p className="text-xs font-medium text-muted-light">{stat.label}</p>
                  <span className="icon-chip h-9 w-9 rounded-lg">
                    <Icon name={stat.icon as IconName} className="h-4 w-4" />
                  </span>
                </div>
                <p className="mt-4 text-[2.125rem] font-semibold leading-none tracking-tight tabular-nums">
                  {stat.value.toString().padStart(2, "0")}
                </p>
              </div>
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
              <ul className="stagger space-y-3">
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
        <Card className="relative overflow-hidden p-8 sm:p-10">
          <span className="icon-chip mb-6 h-12 w-12 rounded-2xl">
            <Icon name="user" />
          </span>
          <h2 className="text-2xl font-semibold tracking-tight">Your account workspace</h2>
          <p className="mt-3 max-w-xl text-[0.9375rem] leading-relaxed text-muted-light">{dashboard.message}</p>
          <ButtonLink href="/profile" variant="secondary" className="mt-6">
            Edit your profile <Icon name="arrow" className="h-4 w-4" />
          </ButtonLink>
        </Card>
      )}
    </div>
  );
}
