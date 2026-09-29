"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { NavBar } from "./NavBar";
import { Spinner } from "./States";
import { useAuth } from "@/lib/auth-context";

const BARE_PATHS = new Set([
  "/",
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
]);

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { loading, user } = useAuth();
  const isBare = BARE_PATHS.has(pathname);
  useEffect(() => {
    if (!isBare && !loading && !user) router.replace("/login");
  }, [isBare, loading, user, router]);
  if (isBare) return <main id="main-content">{children}</main>;
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
          <span>
            Workspace <span className="mx-3 text-navy/25">/</span>{" "}
            <span className="font-medium text-navy">
              {pathname.startsWith("/ideas")
                ? "Business ideas"
                : pathname === "/profile"
                  ? "Profile"
                  : "Overview"}
            </span>
          </span>
          <span className="hidden items-center gap-2 sm:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-brand-500" />
            From idea to opportunity
          </span>
        </div>
        <main id="main-content" tabIndex={-1} className="workspace-main">
          <div key={pathname} className="page-enter">
            {children}
          </div>
        </main>
        <footer className="mx-6 flex flex-wrap justify-between gap-2 border-t border-navy/10 py-5 text-xs text-muted-light lg:mx-10">
          <span>Nashaa · Built for what comes next.</span>
          <span>Demonstration data is fictional.</span>
        </footer>
      </div>
    </div>
  );
}
