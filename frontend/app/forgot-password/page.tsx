"use client";

import { useState } from "react";
import Link from "next/link";

import { Button } from "@/components/Button";
import { AuthLayout } from "@/components/AuthLayout";
import { Input } from "@/components/Input";
import { Alert } from "@/components/States";
import { ApiError, api } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [devToken, setDevToken] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setDone(false);
    setDevToken(null);
    setLoading(true);
    try {
      const res = await api.requestPasswordReset(email);
      setDone(true);
      // In non-production the backend returns a reset token for demo/testing.
      if (res.reset_token) setDevToken(res.reset_token);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not submit the request.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Let's get you back in."
      description="Enter your email to request a single-use password reset link."
    >
      <form onSubmit={handleSubmit} className="mt-6 space-y-4" noValidate>
        {error && <Alert message={error} />}
        {done && (
          <Alert
            kind="success"
            message="If an account exists for this email, a reset link has been sent."
          />
        )}
        <Input
          label="Email"
          type="email"
          name="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <Button type="submit" loading={loading} className="w-full">
          Send reset link
        </Button>
      </form>
      {devToken && (
        <div className="mt-4 rounded-md border border-turquoise-100 bg-turquoise-50 p-3 text-xs text-turquoise-700">
          <p className="font-medium">Demo reset link (testing only)</p>
          <p className="mt-1 break-all">
            <Link
              href={`/reset-password#token=${encodeURIComponent(devToken)}`}
              className="underline"
            >
              Use this link to set a new password
            </Link>
          </p>
          <p className="mt-1 text-turquoise-600">
            This link is shown only in development. In production it would be
            emailed.
          </p>
        </div>
      )}
      <p className="mt-4 text-center text-sm">
        Remembered it?{" "}
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
