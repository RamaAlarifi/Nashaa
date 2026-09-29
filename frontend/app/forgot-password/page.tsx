"use client";

import { useState } from "react";
import Link from "next/link";

import { Button } from "@/components/Button";
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
      setError(err instanceof ApiError ? err.message : "Could not submit the request.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-4 py-8">
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="text-xl font-bold text-gray-900">Reset your password</h1>
        <p className="mt-1 text-sm text-gray-500">
          Enter your email and we'll send a single-use reset link.
        </p>
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
          <div className="mt-4 rounded-md border border-blue-200 bg-blue-50 p-3 text-xs text-blue-700">
            <p className="font-medium">Demo reset link (testing only)</p>
            <p className="mt-1 break-all">
              <Link href={`/reset-password?token=${encodeURIComponent(devToken)}`} className="underline">
                Use this link to set a new password
              </Link>
            </p>
            <p className="mt-1 text-blue-600">
              This link is shown only in development. In production it would be emailed.
            </p>
          </div>
        )}
        <p className="mt-4 text-center text-sm">
          Remembered it?{" "}
          <Link href="/login" className="text-brand-700 hover:underline">
            Back to sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
