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
        <div className="mx-auto flex h-16 max-w-[75rem] items-center justify-between gap-4 px-5 sm:h-[4.5rem] sm:px-8">
          <Link href="/" aria-label="Nashaa home" className="rounded-lg">
            <Logo markClassName="h-8 w-8" />
          </Link>
          <nav aria-label="Primary" className="hidden items-center gap-8 text-sm text-muted-light md:flex">
            <a href="#how" className="transition-colors hover:text-navy">How it works</a>
            <a href="#roles" className="transition-colors hover:text-navy">Who it is for</a>
            <a href="#features" className="transition-colors hover:text-navy">Features</a>
          </nav>
          <div className="flex items-center gap-2">
            <ButtonLink href="/login" variant="ghost" size="sm" className="!text-navy hover:!bg-navy/5">Sign in</ButtonLink>
            <ButtonLink href="/register" size="sm">Get started</ButtonLink>
          </div>
        </div>
      </header>

      <main className="relative z-10">
        <section className="mx-auto max-w-[75rem] px-5 pb-20 pt-14 sm:px-8 sm:pt-20 lg:pb-28">
          <div className="stagger mx-auto max-w-3xl text-center">
            <p className="pill mx-auto">
              <span className="h-1.5 w-1.5 rounded-full bg-turquoise-500" aria-hidden="true" />
              Built for Saudi entrepreneurs
            </p>
            <h1 className="mt-7 text-[2.5rem] font-semibold leading-[1.05] tracking-tight sm:text-6xl lg:text-[4.5rem]">
              From idea to
              <span className="relative ml-3 whitespace-nowrap text-brand-600">
                opportunity
                <svg viewBox="0 0 300 12" className="absolute -bottom-2 left-0 h-3 w-full text-turquoise-500/60" fill="none" aria-hidden="true">
                  <path d="M2 9C60 3 140 2 298 7" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                </svg>
              </span>
              .
            </h1>
            <p className="mx-auto mt-7 max-w-xl text-base leading-relaxed text-muted-light sm:text-lg">
              Nashaa gives your business idea a clear shape, an honest AI assessment,
              and a path to the innovators and investors who can help it grow.
            </p>
            <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <ButtonLink href="/register" size="lg" className="w-full sm:w-auto">
                Create your workspace
                <Icon name="arrow" className="h-4 w-4" />
              </ButtonLink>
              <ButtonLink href="/login" variant="secondary" size="lg" className="w-full sm:w-auto">
                I already have an account
              </ButtonLink>
            </div>
          </div>

          <div className="page-enter relative mx-auto mt-16 max-w-5xl sm:mt-20" aria-hidden="true">
            <div className="preview-window">
              <div className="flex items-center gap-2 border-b border-navy/[0.06] bg-sand-50 px-4 py-3">
                <span className="h-2.5 w-2.5 rounded-full bg-navy/10" />
                <span className="h-2.5 w-2.5 rounded-full bg-navy/10" />
                <span className="h-2.5 w-2.5 rounded-full bg-navy/10" />
                <span className="ml-4 h-5 w-48 rounded-md bg-navy/[0.05]" />
              </div>
              <div className="grid min-h-[21.25rem] grid-cols-[180px_1fr] sm:min-h-[26.25rem] max-sm:grid-cols-1">
                <div className="hidden flex-col gap-2 bg-navy p-5 sm:flex">
                  <span className="mb-4 h-7 w-24 rounded-md bg-white/10" />
                  {[true, false, false, false, false].map((on, i) => (
                    <span key={i} className={`flex items-center gap-2 rounded-lg px-2 py-2 ${on ? "bg-white/10" : ""}`}>
                      <span className={`h-5 w-5 rounded-md ${on ? "bg-turquoise-500/40" : "bg-white/10"}`} />
                      <span className="h-2 w-20 rounded bg-white/15" />
                    </span>
                  ))}
                </div>
                <div className="space-y-5 bg-sand p-5 sm:p-7">
                  <div className="dashboard-hero !rounded-2xl !p-6">
                    <span className="block h-2 w-20 rounded bg-turquoise-400/60" />
                    <span className="mt-4 block h-4 w-56 max-w-full rounded bg-white/80" />
                    <span className="mt-2 block h-4 w-40 rounded bg-white/50" />
                    <span className="mt-5 inline-block h-8 w-32 rounded-lg bg-white" />
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    {["idea", "spark", "lock"].map(icon => (
                      <div key={icon} className="surface flex items-center gap-3 p-3">
                        <span className="icon-chip h-9 w-9"><Icon name={icon as IconName} className="h-4 w-4" /></span>
                        <span className="hidden flex-1 space-y-1.5 sm:block">
                          <span className="block h-3 w-8 rounded bg-navy/70" />
                          <span className="block h-2 w-16 rounded bg-navy/15" />
                        </span>
                      </div>
                    ))}
                  </div>
                  {[0, 1].map(i => (
                    <div key={i} className="surface flex items-center gap-4 p-4">
                      <span className="icon-chip h-10 w-10"><Icon name="idea" className="h-4 w-4" /></span>
                      <span className="flex-1 space-y-2">
                        <span className="block h-2 w-16 rounded bg-brand-500/40" />
                        <span className="block h-3 w-44 max-w-full rounded bg-navy/70" />
                      </span>
                      <span className="hidden rounded-full bg-brand-50 px-3 py-1 text-[0.6875rem] font-medium text-brand-700 ring-1 ring-inset ring-brand-500/20 sm:inline">
                        {i ? "Ready to assess" : "Assessment ready"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="float-slow absolute -left-4 top-1/3 hidden rounded-2xl border border-navy/10 bg-white p-4 shadow-elevated lg:flex lg:items-center lg:gap-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-turquoise-50 text-turquoise-700"><Icon name="spark" className="h-4 w-4" /></span>
              <span className="text-sm font-medium">AI assessment ready</span>
            </div>
            <div className="float-slow absolute -right-4 bottom-12 hidden rounded-2xl border border-navy/10 bg-white p-4 shadow-elevated [animation-delay:1.5s] lg:flex lg:items-center lg:gap-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gold-50 text-gold-700"><Icon name="link" className="h-4 w-4" /></span>
              <span className="text-sm font-medium">New collaboration</span>
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
                <li key={step.title} className="surface p-6">
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
          <div className="surface mt-16 flex flex-col items-start justify-between gap-6 p-8 sm:flex-row sm:items-center sm:p-10">
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
