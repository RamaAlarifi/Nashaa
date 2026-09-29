"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Input, Select, TextArea } from "@/components/Input";
import { Alert, ErrorState, Spinner } from "@/components/States";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import {
  ROLE_LABELS,
  type Profile,
  type ProfileVisibility,
} from "@/lib/types";

export default function ProfilePage() {
  const { user, profile, refresh } = useAuth();
  const [form, setForm] = useState<Profile | null>(profile);
  const [loading, setLoading] = useState(!profile);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        setForm(await api.getProfile());
      } catch (err) {
        setError(
          err instanceof ApiError
            ? err.message
            : "Could not load your profile.",
        );
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  function update<K extends keyof Profile>(key: K, value: Profile[K]) {
    setForm((f) => (f ? { ...f, [key]: value } : f));
    setSuccess(false);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form) return;
    setSaving(true);
    setError(null);
    setSuccess(false);
    setErrors({});
    try {
      await api.updateProfile({
        display_name: form.display_name,
        location: form.location,
        short_description: form.short_description,
        profile_visibility: form.profile_visibility,
        role_specific_info: form.role_specific_info,
      });
      setSuccess(true);
      await refresh();
    } catch (err) {
      if (err instanceof ApiError && err.fieldErrors) {
        const map: Record<string, string> = {};
        err.fieldErrors.forEach((fe) => (map[fe.field] = fe.message));
        setErrors(map);
      } else {
        setError(
          err instanceof ApiError
            ? err.message
            : "Could not save your profile.",
        );
      }
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner label="Loading your profile…" />;
  if (!form && error) return <ErrorState message={error} />;

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="break-words text-3xl font-semibold tracking-tight text-navy">
        Your profile
      </h1>
      <p className="mt-1 text-sm text-muted-light">
        Account role: {user ? ROLE_LABELS[user.role] : "—"} (your role cannot be
        changed here).
      </p>

      <Card className="mt-6 p-6">
        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          {error && <Alert message={error} />}
          {success && <Alert kind="success" message="Profile saved." />}
          <Input
            label="Display name"
            name="display_name"
            required
            value={form?.display_name ?? ""}
            error={errors.display_name}
            onChange={(e) => update("display_name", e.target.value)}
          />
          <Input
            label="Location"
            name="location"
            value={form?.location ?? ""}
            error={errors.location}
            onChange={(e) => update("location", e.target.value)}
          />
          <TextArea
            label="Short description"
            name="short_description"
            rows={4}
            value={form?.short_description ?? ""}
            error={errors.short_description}
            onChange={(e) => update("short_description", e.target.value)}
          />
          {user && ({
            business_owner: [["business_name", "Business name"], ["industry", "Industry"]],
            innovator: [["skills", "Skills"], ["experience", "Professional experience"]],
            investor: [["investment_interests", "Investment interests"], ["preferred_stage", "Preferred business stage"]],
            admin: [],
          }[user.role]).map(([key, label]) => (
            <Input key={key} label={label} name={key} maxLength={2000}
              value={String(form?.role_specific_info[key] ?? "")}
              onChange={(e) => update("role_specific_info", { ...form?.role_specific_info, [key]: e.target.value })} />
          ))}
          <div>
            <Select
              label="Profile visibility"
              name="profile_visibility"
              value={form?.profile_visibility ?? "registered"}
              onChange={(e) =>
                update(
                  "profile_visibility",
                  e.target.value as ProfileVisibility,
                )
              }
            >
              <option value="public">Public</option>
              <option value="registered">Registered users</option>
              <option value="private">Private (only me)</option>
            </Select>
          </div>
          <div className="flex justify-end">
            <Button type="submit" loading={saving}>
              Save profile
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
