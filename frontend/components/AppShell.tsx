"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { NavBar } from "./NavBar";
import { ErrorState, Spinner } from "./States";
import { getToken } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

const BARE_PATHS = new Set([
  "/",
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
]);

const SECTION_TITLES: [string, string][] = [
  ["/ideas", "Business ideas"],
  ["/profile", "Profile"],
  ["/challenges", "Challenges"],
  ["/proposals", "My proposals"],
  ["/verification", "Verification"],
  ["/messages", "Messages"],
  ["/investments", "Investments"],
  ["/collaborations", "Collaborations"],
  ["/leads", "Saved leads"],
  ["/admin", "Administration"],
  ["/reports", "My reports"],
  ["/people", "Discover people"],
  ["/shared-assessments", "Shared assessment"],
];

function sectionTitle(pathname: string) {
  return SECTION_TITLES.find(([href]) => pathname === href || pathname.startsWith(`${href}/`))?.[1] ?? "Overview";
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { loading, user, refresh } = useAuth();
  const isBare = BARE_PATHS.has(pathname);
  useEffect(() => {
    if (!isBare && !loading && !user && !getToken()) router.replace("/login");
  }, [isBare, loading, user, router]);
  if (isBare) return <main id="main-content">{children}</main>;
  if (!loading && !user && getToken()) return <main className="flex min-h-screen items-center justify-center p-6"><ErrorState message="Your session could not be checked. Please retry when the server is available." onRetry={refresh} /></main>;
  if (loading || !user)
    return (
      <main className="flex min-h-screen items-center justify-center">
        <Spinner label="Opening your workspace…" />
      </main>
    );
  return (
    <div className="workspace-shell">
      <a href="#main-content" className="skip-link">
        Skip to content
      </a>
      <NavBar />
      <div className="flex min-w-0 flex-col">
        <div className="workspace-topbar">
          <nav aria-label="Breadcrumb" className="flex min-w-0 items-center gap-2">
            <Link href="/dashboard" className="hidden rounded text-muted-light transition-colors hover:text-navy sm:inline">
              Workspace
            </Link>
            <svg viewBox="0 0 24 24" className="hidden h-3.5 w-3.5 text-navy/25 sm:block" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><path d="m9 6 6 6-6 6" /></svg>
            <span className="truncate text-[0.8125rem] font-semibold text-navy" aria-current="page">
              {sectionTitle(pathname)}
            </span>
          </nav>
          <span className="pill hidden !bg-white/60 sm:inline-flex">
            <span className="relative flex h-2 w-2" aria-hidden="true">
              <span className="absolute inset-0 animate-ping rounded-full bg-brand-500/40 motion-reduce:hidden" />
              <span className="relative h-2 w-2 rounded-full bg-brand-500" />
            </span>
            From idea to opportunity
          </span>
        </div>
        <main id="main-content" tabIndex={-1} className="workspace-main">
          <div key={pathname} className="page-enter">
            {children}
          </div>
        </main>
        <footer className="mx-auto flex w-full max-w-[80rem] flex-wrap justify-between gap-2 border-t border-navy/[0.08] px-5 py-6 text-xs text-muted-light sm:px-6 lg:px-10">
          <span>Nashaa · Built for what comes next.</span>
          <span>Demonstration data is fictional.</span>
        </footer>
      </div>
    </div>
  );
}
