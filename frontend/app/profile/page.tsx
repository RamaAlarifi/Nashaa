"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/Button";
import { Input, Select, TextArea } from "@/components/Input";
import { Alert, ErrorState, Spinner } from "@/components/States";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ROLE_LABELS, type Profile, type ProfileVisibility, type ContactPreference } from "@/lib/types";

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
        setError(err instanceof ApiError ? err.message : "Could not load your profile.");
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
        contact_preference: form.contact_preference,
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
        setError(err instanceof ApiError ? err.message : "Could not save your profile.");
      }
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner label="Loading your profile…" />;
  if (!form && error) return <ErrorState message={error} />;

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900">Your profile</h1>
      <p className="mt-1 text-sm text-gray-500">
        Account role: {user ? ROLE_LABELS[user.role] : "—"} (your role cannot be changed here).
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-5" noValidate>
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
        <div className="grid gap-4 sm:grid-cols-2">
          <Select
            label="Contact preference"
            name="contact_preference"
            value={form?.contact_preference ?? "contact_request"}
            onChange={(e) => update("contact_preference", e.target.value as ContactPreference)}
          >
            <option value="direct_message">Direct messages</option>
            <option value="contact_request">Contact request (accepted first)</option>
          </Select>
          <Select
            label="Profile visibility"
            name="profile_visibility"
            value={form?.profile_visibility ?? "registered"}
            onChange={(e) => update("profile_visibility", e.target.value as ProfileVisibility)}
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
    </div>
  );
}
