"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/Button";
import { IdeaForm, EMPTY_IDEA, type IdeaFormValues } from "@/components/IdeaForm";
import { Alert } from "@/components/States";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function NewIdeaPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [values, setValues] = useState<IdeaFormValues>(EMPTY_IDEA);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [topError, setTopError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  function update<K extends keyof IdeaFormValues>(key: K, value: IdeaFormValues[K]) {
    setValues((v) => ({ ...v, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrors({});
    setTopError(null);
    setSaving(true);
    try {
      const idea = await api.createIdea(values);
      router.push(`/ideas/${idea.id}`);
    } catch (err) {
      if (err instanceof ApiError && err.fieldErrors) {
        const map: Record<string, string> = {};
        err.fieldErrors.forEach((fe) => (map[fe.field] = fe.message));
        setErrors(map);
        setTopError(err.detail ?? null);
      } else {
        setTopError(err instanceof ApiError ? err.message : "Could not save the idea.");
      }
    } finally {
      setSaving(false);
    }
  }

  // Non-business-owners cannot create ideas (server enforces; screen reflects).
  if (user && user.role !== "business_owner") {
    return (
      <div className="mx-auto max-w-xl">
        <Alert
          kind="info"
          message="Only business owners can create business ideas. Your dashboard explains what your role can do."
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900">Create a business idea</h1>
      <p className="mt-1 text-sm text-gray-500">
        Describe your idea. You can edit it later and request an AI assessment.
      </p>
      <form onSubmit={handleSubmit} className="mt-6 space-y-5" noValidate>
        {topError && <Alert message={topError} />}
        <IdeaForm values={values} errors={errors} onChange={update} />
        <div className="flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={() => router.back()}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            Save idea
          </Button>
        </div>
      </form>
    </div>
  );
}
