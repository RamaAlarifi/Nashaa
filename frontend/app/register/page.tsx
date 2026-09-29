"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { Button } from "@/components/Button";
import { AuthLayout } from "@/components/AuthLayout";
import { Input, Select } from "@/components/Input";
import { Alert } from "@/components/States";
import { ApiError, api, setToken } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Role } from "@/lib/types";

const ROLES: { value: Role; label: string }[] = [
  { value: "business_owner", label: "Business owner" },
  { value: "innovator", label: "Innovator" },
  { value: "investor", label: "Investor" },
];

export default function RegisterPage() {
  const router = useRouter();
  const { setUser } = useAuth();
  const [form, setForm] = useState({
    email: "",
    password: "",
    role: "business_owner" as Role,
    display_name: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [topError, setTopError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function update<K extends keyof typeof form>(
    key: K,
    value: (typeof form)[K],
  ) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrors({});
    setTopError(null);
    setLoading(true);
    try {
      const res = await api.register(
        form.email,
        form.password,
        form.role,
        form.display_name,
      );
      setToken(res.token);
      setUser(res.user, res.profile);
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError && err.fieldErrors) {
        const map: Record<string, string> = {};
        err.fieldErrors.forEach((fe) => (map[fe.field] = fe.message));
        setErrors(map);
        setTopError(err.detail ?? null);
      } else if (err instanceof ApiError) {
        setTopError(err.message);
      } else {
        setTopError("Registration failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Start something good."
      description="Create your account and choose the role that fits you. Complete your profile whenever you are ready."
    >
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        {topError && <Alert message={topError} />}
        <Input
          label="Display name"
          name="display_name"
          required
          value={form.display_name}
          error={errors.display_name}
          onChange={(e) => update("display_name", e.target.value)}
        />
        <Input
          label="Email"
          type="email"
          name="email"
          autoComplete="email"
          required
          value={form.email}
          error={errors.email}
          onChange={(e) => update("email", e.target.value)}
        />
        <Input
          label="Password"
          type="password"
          name="password"
          autoComplete="new-password"
          required
          hint="At least 8 characters."
          value={form.password}
          error={errors.password}
          onChange={(e) => update("password", e.target.value)}
        />
        <Select
          label="Account role"
          name="role"
          value={form.role}
          onChange={(e) => update("role", e.target.value as Role)}
        >
          {ROLES.map((r) => (
            <option key={r.value} value={r.value}>
              {r.label}
            </option>
          ))}
        </Select>
        <Button type="submit" loading={loading} className="w-full">
          Create account
        </Button>
      </form>
      <p className="mt-4 text-center text-sm">
        Already have an account?{" "}
        <Link
          href="/login"
          className="font-medium text-brand-700 hover:underline"
        >
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
