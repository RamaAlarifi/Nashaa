"use client";

import { usePathname } from "next/navigation";

import { NavBar } from "@/components/NavBar";
import { useAuth } from "@/lib/auth-context";

// Pages that should NOT show the navbar (auth flows).
const BARE_PATHS = new Set(["/login", "/register", "/forgot-password", "/reset-password"]);

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { loading } = useAuth();
  const isBare = BARE_PATHS.has(pathname);

  if (isBare) {
    return <main className="min-h-screen">{children}</main>;
  }

  return (
    <div className="flex min-h-screen flex-col">
      <NavBar />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6">
        {loading ? (
          <div className="flex items-center justify-center py-16 text-gray-400">Loading…</div>
        ) : (
          children
        )}
      </main>
      <footer className="border-t border-gray-200 bg-white py-4 text-center text-xs text-gray-500">
        Nashaa — Sprint 1 prototype. Data shown is fictional for demonstration.
      </footer>
    </div>
  );
}
