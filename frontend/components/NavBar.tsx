"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Logo } from "./Logo";
import { Icon } from "./Icon";
import { Button } from "./Button";
import { useAuth } from "@/lib/auth-context";
import { ROLE_LABELS } from "@/lib/types";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: "grid" },
  { href: "/ideas", label: "My ideas", icon: "idea" },
  { href: "/profile", label: "My profile", icon: "user" },
] as const;

export function NavBar() {
  const { user, profile, signOut } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [signingOut, setSigningOut] = useState(false);
  const displayName = profile?.display_name || user?.email || "Your workspace";
  async function handleSignOut() {
    setSigningOut(true);
    await signOut();
    router.replace("/login");
  }
  return (
    <header className="workspace-nav">
      <div className="flex items-center justify-between px-6 py-6 lg:px-8 lg:py-9">
        <Link href="/dashboard" aria-label="Nashaa home">
          <Logo variant="reversed" markClassName="h-10 w-10" />
        </Link>
        <button
          type="button"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          aria-controls="workspace-menu"
          aria-label="Toggle navigation menu"
          className="flex h-11 w-11 items-center justify-center rounded-xl border border-white/20 text-white lg:hidden"
        >
          <svg
            viewBox="0 0 24 24"
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            aria-hidden="true"
          >
            <path
              d={open ? "M6 6l12 12M18 6L6 18" : "M4 7h16M4 12h16M4 17h16"}
            />
          </svg>
        </button>
      </div>
      <div
        id="workspace-menu"
        className={`${open ? "flex" : "hidden"} min-h-0 flex-1 flex-col px-5 pb-6 lg:flex`}
      >
        <p className="eyebrow mb-4 mt-3 px-4 text-navy-100/80">Workspace</p>
        <nav aria-label="Main navigation">
          <ul className="space-y-2">
            {NAV_ITEMS.filter((item) => item.href !== "/ideas" || user?.role === "business_owner").map(({ href, label, icon }) => {
              const active =
                pathname === href || pathname.startsWith(`${href}/`);
              return (
                <li key={href}>
                  <Link
                    href={href}
                    onClick={() => setOpen(false)}
                    aria-current={active ? "page" : undefined}
                    className={`nav-link ${active ? "nav-link-active" : ""}`}
                  >
                    <Icon name={icon} />
                    {label}
                    {active && (
                      <span className="ml-auto h-1.5 w-1.5 rounded-full bg-turquoise-400" />
                    )}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
        <div className="mt-auto pt-10">
          <div className="mb-6 hidden rounded-2xl border border-white/10 bg-white/[0.03] p-5 lg:block">
            <Icon name="spark" className="mb-3 h-6 w-6 text-turquoise-400" />
            <p className="text-sm font-medium text-white">
              Small steps. Real progress.
            </p>
            <p className="mt-2 text-xs leading-relaxed text-navy-100">
              Give your next idea the space to grow.
            </p>
          </div>
          <div className="flex min-w-0 items-center gap-3 border-t border-white/10 pt-6">
            <span
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-turquoise-500/15 text-sm font-semibold text-turquoise-400"
              aria-hidden="true"
            >
              {displayName.slice(0, 1).toUpperCase()}
            </span>
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-white">
                {displayName}
              </p>
              <p className="mt-1 text-xs text-navy-100">
                {user ? ROLE_LABELS[user.role] : "Nashaa"}
              </p>
            </div>
          </div>
          <Button
            type="button"
            variant="ghost"
            loading={signingOut}
            onClick={handleSignOut}
            className="mt-4 w-full !text-navy-100 hover:!bg-white/10"
          >
            <Icon name="logout" className="h-4 w-4" />
            Sign out
          </Button>
        </div>
      </div>
    </header>
  );
}
