"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ButtonLink } from "@/components/Button";
import { Icon, type IconName } from "@/components/Icon";
import { Logo } from "@/components/Logo";
import { Spinner } from "@/components/States";
import { useAuth } from "@/lib/auth-context";

const ROLES: { title: string; text: string; icon: IconName }[] = [
  { title: "Business owners", text: "Shape ideas, run an AI business assessment, post challenges and find collaborators.", icon: "idea" },
  { title: "Innovators", text: "Discover real business challenges, submit proposals and grow collaborations.", icon: "spark" },
  { title: "Investors", text: "Follow promising opportunities and manage your investment workspace.", icon: "trend" },
];

const FEATURES: { title: string; text: string; icon: IconName }[] = [
  { title: "AI business assessment", text: "A structured look at market, customers, risks and next steps for every idea revision.", icon: "spark" },
  { title: "Challenges and proposals", text: "Owners publish challenges; innovators answer with proposals that can become collaborations.", icon: "target" },
  { title: "Verified participants", text: "Account verification keeps the community credible for everyone involved.", icon: "shield" },
  { title: "Messages and discovery", text: "Find the right people and keep every conversation in one calm place.", icon: "chat" },
];

const STEPS = [
  { title: "Capture", text: "Describe the problem, the customer and your stage. Keep it private until you are ready." },
  { title: "Assess", text: "Generate an AI assessment and refine the idea revision by revision." },
  { title: "Connect", text: "Share selectively, meet innovators and investors, and move together." },
];

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();
  useEffect(() => {
    if (!loading && user) router.replace("/dashboard");
  }, [user, loading, router]);
  if (loading || user)
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner label="Opening Nashaa…" />
      </div>
    );
  return (
    <div className="landing">
      <div className="landing-hero-bg" aria-hidden="true" />
      <header className="landing-nav">
        <div className="landing-nav-inner mx-auto max-w-[75rem] px-4 sm:px-8">
          <Link href="/" aria-label="Nashaa home" className="landing-logo rounded-lg">
            <Logo className="!p-0" />
          </Link>
          <nav aria-label="Primary" className="landing-links text-sm text-muted-light">
            <a href="#how" className="landing-section-link rounded-md hover:text-navy">How it works</a>
            <a href="#roles" className="landing-section-link rounded-md hover:text-navy">Who it is for</a>
            <a href="#features" className="landing-section-link rounded-md hover:text-navy">Features</a>
          </nav>
          <div className="landing-account flex items-center gap-1 sm:gap-2">
            <ButtonLink href="/login" variant="ghost" size="sm" className="!text-navy hover:!bg-navy/5">Sign in</ButtonLink>
            <ButtonLink href="/register" size="sm">Get started</ButtonLink>
          </div>
        </div>
      </header>

      <main className="relative z-10">
        <section className="mx-auto max-w-[75rem] px-5 pb-16 pt-12 sm:px-8 sm:pt-20 lg:pb-24">
          <div className="stagger mx-auto max-w-[50rem] text-center">
            <p className="pill mx-auto">
              <span className="h-1.5 w-1.5 rounded-full bg-turquoise-500" aria-hidden="true" />
              Built for Saudi entrepreneurs
            </p>
            <h1 className="landing-title mt-6 font-semibold">
              From idea to{" "}
              <span className="relative inline-block whitespace-nowrap text-brand-700">
                opportunity.
                <svg viewBox="0 0 300 12" className="absolute -bottom-2 left-0 h-3 w-full text-turquoise-500/60" fill="none" aria-hidden="true">
                  <path d="M2 9C60 3 140 2 298 7" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                </svg>
              </span>
            </h1>
            <p className="mx-auto mt-6 max-w-[38rem] text-base leading-relaxed text-muted-light sm:text-[1.1875rem]">
              Nashaa gives your business idea a clear shape, an honest AI assessment,
              and a path to the innovators and investors who can help it grow.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <ButtonLink href="/register" size="lg" className="w-full sm:w-auto">
                Create your workspace
                <Icon name="arrow" className="h-4 w-4" />
              </ButtonLink>
              <ButtonLink href="/login" variant="secondary" size="lg" className="w-full sm:w-auto">
                I already have an account
              </ButtonLink>
            </div>
          </div>

          <div className="landing-preview page-enter relative mx-auto mt-12 max-w-[68rem] sm:mt-16" aria-hidden="true">
            <div className="preview-window">
              <div className="flex items-center gap-2 border-b border-navy/10 bg-sand-50 px-4 py-3.5 sm:px-5">
                <span className="h-2 w-2 rounded-full bg-navy/15" />
                <span className="h-2 w-2 rounded-full bg-navy/15" />
                <span className="h-2 w-2 rounded-full bg-navy/15" />
                <span className="ml-3 text-xs font-medium text-muted-light">Workspace preview</span>
              </div>
              <div className="grid sm:grid-cols-[10.5rem_minmax(0,1fr)]">
                <div className="hidden flex-col gap-2 bg-navy px-4 py-6 sm:flex">
                  <Logo variant="reversed" className="mb-4 !p-0" />
                  {([
                    ["grid", "Overview"],
                    ["idea", "My ideas"],
                    ["chat", "Messages"],
                  ] as const).map(([icon, label], i) => (
                    <div key={label} className={`flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-xs ${i === 0 ? "bg-white/10 text-white" : "text-white/75"}`}>
                      <Icon name={icon} className="h-4 w-4 shrink-0" />
                      {label}
                    </div>
                  ))}
                </div>
                <div className="min-w-0 space-y-4 bg-sand p-4 sm:p-6">
                  <div className="dashboard-hero !rounded-2xl !p-5 sm:!p-7">
                    <p className="eyebrow text-turquoise-400">Business owner workspace</p>
                    <p className="mt-2 text-xl font-semibold text-white sm:text-2xl">Give your idea a clear next step.</p>
                    <p className="mt-2 max-w-md text-sm leading-relaxed text-white/80">Assess the opportunity, refine your plan, and find the right people to work with.</p>
                  </div>
                  <div className="grid gap-2 sm:grid-cols-3">
                    {([
                      ["idea", "Business ideas"],
                      ["spark", "AI assessments"],
                      ["link", "Collaborations"],
                    ] as const).map(([icon, label]) => (
                      <div key={label} className="surface flex min-w-0 items-center gap-2.5 p-2.5 lg:p-3">
                        <span className="icon-chip h-8 w-8 shrink-0"><Icon name={icon} className="h-4 w-4" /></span>
                        <span className="text-xs font-medium leading-snug text-navy">{label}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="how" className="scroll-mt-24 border-y border-navy/[0.06] bg-white/60">
          <div className="mx-auto grid max-w-[75rem] gap-12 px-5 py-20 sm:px-8 lg:grid-cols-[1fr_1.4fr] lg:py-28">
            <div>
              <p className="eyebrow text-brand-700">How it works</p>
              <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
                Three calm steps from a thought to a plan.
              </h2>
              <p className="mt-4 max-w-sm text-[0.9375rem] leading-relaxed text-muted-light">
                You do not need all the answers. Start with the problem and let the workspace guide what comes next.
              </p>
            </div>
            <ol className="stagger grid gap-4 sm:grid-cols-3">
              {STEPS.map((step, i) => (
                <li key={step.title} className="surface landing-step p-5 sm:p-6">
                  <span className="step-index">0{i + 1}</span>
                  <h3 className="mt-6 text-lg font-semibold">{step.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-light">{step.text}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section id="roles" className="scroll-mt-24 px-3 py-3 sm:px-5 sm:py-5">
          <div className="dashboard-hero mx-auto max-w-[77.5rem] !rounded-[32px] !px-6 !py-16 sm:!px-12 lg:!py-24">
            <div className="relative z-10 mx-auto max-w-[67.5rem]">
              <p className="eyebrow text-turquoise-400">Who it is for</p>
              <h2 className="mt-4 max-w-xl text-3xl font-medium tracking-tight text-white sm:text-4xl">
                One workspace, shaped around your role.
              </h2>
              <div className="stagger mt-12 grid gap-4 md:grid-cols-3">
                {ROLES.map(role => (
                  <div key={role.title} className="role-card">
                    <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-turquoise-500/15 text-turquoise-400">
                      <Icon name={role.icon} />
                    </span>
                    <h3 className="mt-3 text-lg font-semibold text-white">{role.title}</h3>
                    <p className="text-sm leading-relaxed text-navy-100/80">{role.text}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="mx-auto max-w-[75rem] scroll-mt-24 px-5 py-20 sm:px-8 lg:py-28">
          <div className="max-w-2xl">
            <p className="eyebrow text-brand-700">Features</p>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
              Everything an early idea needs, nothing it does not.
            </h2>
          </div>
          <div className="stagger mt-12 grid gap-4 sm:grid-cols-2">
            {FEATURES.map(feature => (
              <div key={feature.title} className="feature-card">
                <span className="icon-chip"><Icon name={feature.icon} /></span>
                <div>
                  <h3 className="text-lg font-semibold tracking-tight">{feature.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-light">{feature.text}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="surface landing-cta mt-12 flex flex-col items-start justify-between gap-6 p-8 sm:flex-row sm:items-center sm:p-10">
            <div>
              <h2 className="text-2xl font-semibold tracking-tight">Ready to give your idea some momentum?</h2>
              <p className="mt-2 text-sm text-muted-light">Create your workspace and start with your first idea.</p>
            </div>
            <ButtonLink href="/register" size="lg">
              Get started
              <Icon name="arrow" className="h-4 w-4" />
            </ButtonLink>
          </div>
        </section>
      </main>

      <footer className="relative z-10 border-t border-navy/[0.06]">
        <div className="mx-auto flex max-w-[75rem] flex-col justify-between gap-4 px-5 py-8 text-xs text-muted-light sm:flex-row sm:items-center sm:px-8">
          <Logo markClassName="h-6 w-6" />
          <span>Nashaa · Built for what comes next. Demonstration data is fictional.</span>
        </div>
      </footer>
    </div>
  );
}
