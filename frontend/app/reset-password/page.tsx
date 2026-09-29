"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";

import { Button } from "@/components/Button";
import { AuthLayout } from "@/components/AuthLayout";
import { Input } from "@/components/Input";
import { Alert } from "@/components/States";
import { ApiError, api } from "@/lib/api";

function ResetForm() {
  const router = useRouter();
  const params = useSearchParams();
  const [token, setToken] = useState(params.get("token") ?? "");
  useEffect(() => {
    const fragment = new URLSearchParams(window.location.hash.slice(1));
    if (fragment.get("token")) setToken(fragment.get("token")!);
    window.history.replaceState(null, "", "/reset-password");
  }, []);
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setDone(false);
    setLoading(true);
    try {
      await api.confirmPasswordReset(token, newPassword);
      setDone(true);
      setTimeout(() => router.push("/login"), 1500);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not reset the password.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="A fresh start."
      description="Use the single-use reset link or code from your email to set a new password."
    >
      <form onSubmit={handleSubmit} className="mt-6 space-y-4" noValidate>
        {error && <Alert message={error} />}
        {done && (
          <Alert
            kind="success"
            message="Password reset. Redirecting to sign in…"
          />
        )}
        <Input
          label="Reset token"
          name="token"
          required
          value={token}
          onChange={(e) => setToken(e.target.value)}
        />
        <Input
          label="New password"
          type="password"
          name="new_password"
          autoComplete="new-password"
          required
          hint="At least 8 characters."
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
        />
        <Button type="submit" loading={loading} className="w-full">
          Reset password
        </Button>
      </form>
      <p className="mt-4 text-center text-sm">
        <Link
          href="/login"
          className="font-medium text-brand-700 hover:underline"
        >
          Back to sign in
        </Link>
      </p>
    </AuthLayout>
  );
}

export default function ResetPasswordPage() {
  // useSearchParams must be wrapped in Suspense for static generation.
  return (
    <Suspense
      fallback={
        <div className="p-8 text-center text-muted-light">Loading…</div>
      }
    >
      <ResetForm />
    </Suspense>
  );
}
