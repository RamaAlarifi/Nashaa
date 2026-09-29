"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth-context";

export function NavBar() {
  const { user, profile, signOut } = useAuth();
  const router = useRouter();
  const displayName = profile?.display_name ?? user?.email ?? "";

  async function handleSignOut() {
    await signOut();
    router.push("/login");
  }

  return (
    <header className="border-b border-gray-200 bg-white">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link href="/dashboard" className="flex items-center gap-2 font-bold text-brand-700">
          <span className="inline-flex h-7 w-7 items-center justify-center rounded-md bg-brand-600 text-white">
            N
          </span>
          Nashaa
        </Link>
        {user ? (
          <div className="flex items-center gap-4">
            <span className="hidden text-sm text-gray-600 sm:inline" aria-label="Signed in as">
              {displayName}
            </span>
            <Link href="/profile" className="text-sm font-medium text-gray-700 hover:text-brand-700">
              Profile
            </Link>
            <Link href="/dashboard" className="text-sm font-medium text-gray-700 hover:text-brand-700">
              Dashboard
            </Link>
            <button
              type="button"
              onClick={handleSignOut}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Sign out
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm font-medium text-gray-700 hover:text-brand-700">
              Sign in
            </Link>
            <Link
              href="/register"
              className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700"
            >
              Create account
            </Link>
          </div>
        )}
      </nav>
    </header>
  );
}
