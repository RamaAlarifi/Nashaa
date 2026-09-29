"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { Button } from "@/components/Button";
import { AuthLayout } from "@/components/AuthLayout";
import { Input } from "@/components/Input";
import { Alert } from "@/components/States";
import { ApiError, api, setToken } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { setUser } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.login(email, password);
      setToken(res.token);
      setUser(res.user, res.profile);
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      else setError("Sign in failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Welcome back."
      description="Sign in to give your next idea a little momentum."
    >
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        {error && <Alert message={error} />}
        <Input
          label="Email"
          type="email"
          name="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <Input
          label="Password"
          type="password"
          name="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Button type="submit" loading={loading} className="w-full">
          Sign in
        </Button>
      </form>
      <div className="mt-4 flex items-center justify-between text-sm">
        <Link
          href="/forgot-password"
          className="font-medium text-brand-700 hover:underline"
        >
          Forgot password?
        </Link>
        <Link
          href="/register"
          className="font-medium text-brand-700 hover:underline"
        >
          Create account
        </Link>
      </div>
    </AuthLayout>
  );
}
