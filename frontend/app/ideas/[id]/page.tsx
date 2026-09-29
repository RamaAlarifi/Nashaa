"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

import { Button } from "@/components/Button";
import { IdeaForm, ideaToForm, type IdeaFormValues } from "@/components/IdeaForm";
import { Alert, ErrorState, EmptyState, Spinner } from "@/components/States";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import {
  STAGE_LABELS,
  VISIBILITY_LABELS,
  type AssessmentStatusResponse,
  type BusinessIdea,
  type IdeaVisibility,
} from "@/lib/types";

export default function IdeaDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const [idea, setIdea] = useState<BusinessIdea | null>(null);
  const [assessment, setAssessment] = useState<AssessmentStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [editing, setEditing] = useState(false);
  const [values, setValues] = useState<IdeaFormValues | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [topError, setTopError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savingVisibility, setSavingVisibility] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [assessError, setAssessError] = useState<string | null>(null);

  const loadIdea = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getIdea(params.id);
      // Only full-detail ideas are editable. A summary (non-owner) has no
      // 'problem' field and means this idea is not the viewer's.
      if (!("problem" in res)) {
        setIdea(null);
        setError("This idea is private, or you can only view a limited summary.");
        return;
      }
      setIdea(res);
      setValues(ideaToForm(res));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load the idea.");
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  const loadAssessment = useCallback(async () => {
    try {
      setAssessment(await api.getAssessmentStatus(params.id));
    } catch (err) {
      setAssessError(err instanceof ApiError ? err.message : "Could not load assessment status.");
    }
  }, [params.id]);

  useEffect(() => {
    loadIdea();
    loadAssessment();
  }, [loadIdea, loadAssessment]);

  function update<K extends keyof IdeaFormValues>(key: K, value: IdeaFormValues[K]) {
    setValues((v) => (v ? { ...v, [key]: value } : v));
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!values) return;
    setFormErrors({});
    setTopError(null);
    setSaving(true);
    try {
      const updated = await api.updateIdea(params.id, values);
      setIdea(updated);
      setValues(ideaToForm(updated));
      setEditing(false);
      await loadAssessment();
    } catch (err) {
      if (err instanceof ApiError && err.fieldErrors) {
        const map: Record<string, string> = {};
        err.fieldErrors.forEach((fe) => (map[fe.field] = fe.message));
        setFormErrors(map);
        setTopError(err.detail ?? null);
      } else {
        setTopError(err instanceof ApiError ? err.message : "Could not save the idea.");
      }
    } finally {
      setSaving(false);
    }
  }

  async function handleVisibility(newVis: IdeaVisibility) {
    setSavingVisibility(true);
    try {
      const updated = await api.setVisibility(params.id, newVis);
      setIdea(updated);
    } catch (err) {
      setTopError(err instanceof ApiError ? err.message : "Could not change visibility.");
    } finally {
      setSavingVisibility(false);
    }
  }

  async function handleGenerate() {
    setAssessError(null);
    setGenerating(true);
    try {
      const res = await api.generateAssessment(params.id);
      setAssessment(res);
      // If a generation just started/succeeded, reload idea (revision may bump).
      await loadIdea();
      await loadAssessment();
    } catch (err) {
      setAssessError(err instanceof ApiError ? err.message : "Assessment failed.");
    } finally {
      setGenerating(false);
    }
  }

  async function handleDelete() {
    if (!confirm("Delete this idea and all its assessments? This cannot be undone.")) return;
    try {
      await api.deleteIdea(params.id);
      router.push("/ideas");
    } catch (err) {
      setTopError(err instanceof ApiError ? err.message : "Could not delete the idea.");
    }
  }

  if (loading) return <Spinner label="Loading the idea…" />;
  if (error || !idea)
    return (
      <div className="space-y-4">
        <ErrorState message={error ?? "Could not load the idea."} onRetry={loadIdea} />
        <Link href="/ideas" className="text-sm text-brand-700 hover:underline">
          ← Back to ideas
        </Link>
      </div>
    );

  const isOwner = user?.id === idea.owner_id;
  const latestValid = assessment?.latest_valid;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{idea.name}</h1>
          <p className="text-sm text-gray-500">
            {idea.industry || "No industry"} · {STAGE_LABELS[idea.business_stage]} · Revision{" "}
            {idea.revision_number}
          </p>
        </div>
        <Link href="/ideas" className="text-sm text-brand-700 hover:underline">
          ← Back
        </Link>
      </div>

      {topError && <Alert message={topError} />}

      {/* Visibility setting (screen 12) */}
      {isOwner && (
        <section className="rounded-lg border border-gray-200 bg-white p-4">
          <h2 className="text-sm font-semibold text-gray-700">Who can see this idea</h2>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {(Object.keys(VISIBILITY_LABELS) as IdeaVisibility[]).map((v) => (
              <button
                key={v}
                type="button"
                disabled={savingVisibility || idea.visibility === v}
                onClick={() => handleVisibility(v)}
                className={`rounded-md border px-3 py-1.5 text-sm ${
                  idea.visibility === v
                    ? "border-brand-600 bg-brand-50 text-brand-700"
                    : "border-gray-300 text-gray-700 hover:bg-gray-50"
                } disabled:opacity-50`}
              >
                {VISIBILITY_LABELS[v]}
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Idea details / edit (screens 9) */}
      <section className="rounded-lg border border-gray-200 bg-white p-5">
        {isOwner && !editing ? (
          <div className="space-y-3">
            <div className="flex justify-end">
              <Button variant="secondary" onClick={() => setEditing(true)}>
                Edit idea
              </Button>
            </div>
            <IdeaReadOnly idea={idea} />
          </div>
        ) : editing && values ? (
          <form onSubmit={handleSave} className="space-y-5">
            <h2 className="text-lg font-semibold text-gray-800">Edit idea</h2>
            <IdeaForm values={values} errors={formErrors} onChange={update} />
            <div className="flex justify-end gap-3">
              <Button type="button" variant="secondary" onClick={() => setEditing(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={saving}>
                Save changes
              </Button>
            </div>
          </form>
        ) : (
          <IdeaReadOnly idea={idea} />
        )}
      </section>

      {/* Assessment workspace + result (screens 10, 11) — owner only */}
      {isOwner && (
        <section className="rounded-lg border border-gray-200 bg-white p-5">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-800">AI business assessment</h2>
            <Button onClick={handleGenerate} loading={generating} disabled={generating}>
              {assessment?.in_progress
                ? "Generating…"
                : latestValid
                ? "Regenerate assessment"
                : "Generate assessment"}
            </Button>
          </div>

          {assessError && <div className="mt-3"><Alert message={assessError} /></div>}

          <AssessmentPanel status={assessment} loading={loading} />
        </section>
      )}

      {isOwner && (
        <div className="flex justify-end">
          <Button variant="danger" onClick={handleDelete}>
            Delete idea
          </Button>
        </div>
      )}
    </div>
  );
}

function IdeaReadOnly({ idea }: { idea: BusinessIdea }) {
  return (
    <dl className="grid gap-x-6 gap-y-3 sm:grid-cols-2">
      <Field label="Problem" value={idea.problem} full />
      <Field label="Solution" value={idea.solution} full />
      <Field label="Industry" value={idea.industry} />
      <Field label="Stage" value={STAGE_LABELS[idea.business_stage]} />
      <Field label="Target location" value={idea.target_location} />
      <Field label="Budget" value={idea.budget} />
      <Field label="Intended customers" value={idea.intended_customers} full />
      <Field label="Current challenges" value={idea.current_challenges} full />
      <Field label="Visibility" value={VISIBILITY_LABELS[idea.visibility]} />
    </dl>
  );
}

function Field({ label, value, full }: { label: string; value: string; full?: boolean }) {
  return (
    <div className={full ? "sm:col-span-2" : ""}>
      <dt className="text-xs font-medium uppercase text-gray-400">{label}</dt>
      <dd className="mt-0.5 whitespace-pre-wrap text-sm text-gray-800">{value || "—"}</dd>
    </div>
  );
}

function AssessmentPanel({
  status,
  loading,
}: {
  status: AssessmentStatusResponse | null;
  loading: boolean;
}) {
  if (loading || !status) return <div className="mt-4"><Spinner label="Loading assessment…" /></div>;

  if (status.current_status === "in_progress") {
    return (
      <div className="mt-4">
        <Alert kind="info" message="Assessment is being generated. Please wait…" />
        <Spinner label="Generating assessment…" />
      </div>
    );
  }

  if (status.current_status === "none") {
    return (
      <div className="mt-4">
        <EmptyState
          title="No assessment yet"
          description="Generate an AI-assessed analysis of this idea. Assumptions and uncertain information will be clearly labeled."
        />
      </div>
    );
  }

  return (
    <div className="mt-4 space-y-4">
      {status.current_status === "failed" && status.error_message && (
        <Alert message={`Last attempt failed: ${status.error_message}`} />
      )}
      {status.latest_valid ? (
        <div className="space-y-4">
          <p className="text-xs text-gray-400">
            Generated from idea revision {status.latest_valid.idea_revision}
          </p>
          <AssessmentSection title="Market considerations" text={status.latest_valid.market_considerations} />
          <AssessmentSection title="Target customers" text={status.latest_valid.target_customer_analysis} />
          <AssessmentSection title="Competitors" text={status.latest_valid.competitor_considerations} />
          <AssessmentSection title="Indicative costs" text={status.latest_valid.indicative_costs} />
          <AssessmentSection title="Suggested next steps" text={status.latest_valid.suggested_next_steps} />
          <AssessmentSection title="Assumptions" text={status.latest_valid.assumptions} highlight />
          <AssessmentSection title="Sources" text={status.latest_valid.sources} />
        </div>
      ) : (
        <EmptyState
          title="No successful assessment yet"
          description="The last attempt failed. Try generating again."
        />
      )}
    </div>
  );
}

function AssessmentSection({
  title,
  text,
  highlight,
}: {
  title: string;
  text: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-md border p-4 ${
        highlight ? "border-amber-200 bg-amber-50" : "border-gray-200 bg-gray-50"
      }`}
    >
      <h3 className={`text-sm font-semibold ${highlight ? "text-amber-800" : "text-gray-700"}`}>
        {title}
      </h3>
      <p className="mt-1 whitespace-pre-wrap text-sm text-gray-800">{text || "—"}</p>
    </div>
  );
}
