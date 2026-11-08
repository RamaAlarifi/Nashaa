"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Logo } from "./Logo";
import { Icon, type IconName } from "./Icon";
import { Button } from "./Button";
import { useAuth } from "@/lib/auth-context";
import { ROLE_LABELS } from "@/lib/types";

type NavItem = { href: string; label: string; icon: IconName; group: "Workspace" | "Connect" | "Account" };

const NAV_ITEMS: readonly NavItem[] = [
  { href: "/dashboard", label: "Overview", icon: "grid", group: "Workspace" },
  { href: "/ideas", label: "My ideas", icon: "idea", group: "Workspace" },
  { href: "/challenges", label: "Challenges", icon: "target", group: "Workspace" },
  { href: "/proposals", label: "My proposals", icon: "file", group: "Workspace" },
  { href: "/investments", label: "Investments", icon: "trend", group: "Workspace" },
  { href: "/collaborations", label: "Collaborations", icon: "link", group: "Workspace" },
  { href: "/leads", label: "Saved leads", icon: "bookmark", group: "Workspace" },
  { href: "/messages", label: "Messages", icon: "chat", group: "Connect" },
  { href: "/people", label: "Discover people", icon: "users", group: "Connect" },
  { href: "/profile", label: "My profile", icon: "user", group: "Account" },
  { href: "/verification", label: "Verification", icon: "shield", group: "Account" },
  { href: "/reports", label: "My reports", icon: "flag", group: "Account" },
  { href: "/admin", label: "Administration", icon: "lock", group: "Account" },
];

const GROUPS = ["Workspace", "Connect", "Account"] as const;

export function NavBar() {
  const { user, profile, signOut } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [signingOut, setSigningOut] = useState(false);
  const displayName = profile?.display_name || user?.email || "Your workspace";
  useEffect(() => setOpen(false), [pathname]);
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);
  async function handleSignOut() {
    setSigningOut(true);
    await signOut();
    router.replace("/login");
  }
  const visible = NAV_ITEMS.filter(item => {
    if (item.href === "/collaborations") return user?.role === "business_owner" || user?.role === "innovator";
    if (item.href === "/leads") return user?.role === "business_owner";
    if (item.href === "/admin") return user?.role === "admin";
    if (item.href === "/ideas") return user?.role === "business_owner";
    if (item.href === "/challenges") return user?.role === "business_owner" || user?.role === "innovator";
    if (item.href === "/proposals") return user?.role === "innovator";
    if (item.href === "/investments") return user?.role === "investor";
    if (item.href === "/messages") return user?.role !== "admin";
    if (item.href === "/people") return user?.role !== "admin";
    return true;
  });
  return (
    <header className="workspace-nav">
      <div className="flex items-center justify-between px-5 py-4 lg:px-6 lg:pb-4 lg:pt-7">
        <Link href="/dashboard" aria-label="Nashaa home" className="rounded-lg">
          <Logo variant="reversed" markClassName="h-9 w-9" />
        </Link>
        <button
          type="button"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          aria-controls="workspace-menu"
          aria-label="Toggle navigation menu"
          className="flex h-11 w-11 items-center justify-center rounded-xl border border-white/15 bg-white/[0.04] text-white transition-colors hover:bg-white/10 lg:hidden"
        >
          <Icon name={open ? "close" : "menu"} />
        </button>
      </div>
      <div
        id="workspace-menu"
        className={`${open ? "nav-drawer flex max-h-[calc(100dvh-76px)] overflow-y-auto" : "hidden"} min-h-0 flex-1 flex-col px-4 pb-5 lg:flex lg:max-h-none lg:px-5`}
      >
        <nav aria-label="Main navigation" className="flex-1">
          {GROUPS.map(group => {
            const items = visible.filter(item => item.group === group);
            if (!items.length) return null;
            return (
              <div key={group}>
                <p className="nav-section-label">{group}</p>
                <ul className="space-y-0.5">
                  {items.map(({ href, label, icon }) => {
                    const active = pathname === href || pathname.startsWith(`${href}/`);
                    return (
                      <li key={href}>
                        <Link
                          href={href}
                          onClick={() => setOpen(false)}
                          aria-current={active ? "page" : undefined}
                          className={`nav-link ${active ? "nav-link-active" : ""}`}
                        >
                          <span className="nav-icon">
                            <Icon name={icon} className="h-[1.125rem] w-[1.125rem]" />
                          </span>
                          {label}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </div>
            );
          })}
        </nav>
        <div className="mt-8">
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-3">
            <div className="flex min-w-0 items-center gap-3">
              <span
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-turquoise-500/30 to-brand-500/30 text-sm font-semibold text-white ring-1 ring-inset ring-white/15"
                aria-hidden="true"
              >
                {displayName.slice(0, 1).toUpperCase()}
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-white">{displayName}</p>
                <p className="mt-0.5 flex items-center gap-1.5 text-xs text-navy-100/70">
                  <span className="h-1.5 w-1.5 rounded-full bg-turquoise-400" aria-hidden="true" />
                  {user ? ROLE_LABELS[user.role] : "Nashaa"}
                </p>
              </div>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              loading={signingOut}
              onClick={handleSignOut}
              className="mt-3 w-full !justify-start !text-navy-100/80 hover:!bg-white/[0.08] hover:!text-white"
            >
              <Icon name="logout" className="h-4 w-4" />
              Sign out
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
