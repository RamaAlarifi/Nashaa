"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

import { AssessmentLoading } from "@/components/AssessmentLoading";
import { Button } from "@/components/Button";
import { IndustryLabel } from "@/lib/industries";
import { IdeaOpportunities } from "@/components/IdeaOpportunities";
import { Card } from "@/components/Card";
import {
  IdeaForm,
  ideaToForm,
  type IdeaFormValues,
} from "@/components/IdeaForm";
import { Alert, ErrorState, EmptyState, Spinner } from "@/components/States";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import {
  STAGE_LABELS,
  VISIBILITY_LABELS,
  type AssessmentStatusResponse,
  type BusinessIdea,
  type BusinessIdeaSummary,
  type IdeaVisibility,
} from "@/lib/types";

export default function IdeaDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const [idea, setIdea] = useState<BusinessIdea | null>(null);
  const [summary, setSummary] = useState<BusinessIdeaSummary | null>(null);
  const [assessment, setAssessment] = useState<AssessmentStatusResponse | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [editing, setEditing] = useState(false);
  const [values, setValues] = useState<IdeaFormValues | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [topError, setTopError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savingVisibility, setSavingVisibility] = useState(false);
  const [generating, setGenerating] = useState(false);
  const generationPending = useRef(false);
  const assessmentBusy = generating || Boolean(assessment?.in_progress);
  const [assessError, setAssessError] = useState<string | null>(null);
  const [assessmentLoading, setAssessmentLoading] = useState(true);

  const loadIdea = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getIdea(params.id);
      // Only full-detail ideas are editable. A summary (non-owner) has no
      // 'problem' field and means this idea is not the viewer's.
      if (!("problem" in res)) {
        setIdea(null);
        setSummary(res);
        setAssessmentLoading(false);
        return;
      }
      setSummary(null);
      setIdea(res);
      setValues(ideaToForm(res));
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not load the idea.",
      );
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  const loadAssessment = useCallback(async () => {
    try {
      setAssessment(await api.getAssessmentStatus(params.id));
      setAssessError(null);
    } catch (err) {
      setAssessError(
        err instanceof ApiError
          ? err.message
          : "Could not load assessment status.",
      );
    } finally {
      setAssessmentLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    loadIdea();
  }, [loadIdea]);

  useEffect(() => {
    if (idea) loadAssessment();
  }, [idea, loadAssessment]);

  useEffect(() => {
    if (!assessment?.in_progress) return;
    const timer = window.setInterval(loadAssessment, 3000);
    return () => window.clearInterval(timer);
  }, [assessment?.in_progress, loadAssessment]);

  function update<K extends keyof IdeaFormValues>(
    key: K,
    value: IdeaFormValues[K],
  ) {
    setValues((v) => (v ? { ...v, [key]: value } : v));
  }

  async function handleSave(e: React.SyntheticEvent, assess = false) {
    e.preventDefault();
    if (!values || saving || assessmentBusy || generationPending.current) return;
    setFormErrors({});
    setTopError(null);
    setSaving(true);
    try {
      const updated = await api.updateIdea(params.id, values);
      setIdea(updated);
      setValues(ideaToForm(updated));
      setEditing(false);
      if (assess) await handleGenerate();
      else await loadAssessment();
    } catch (err) {
      if (err instanceof ApiError && err.fieldErrors) {
        const map: Record<string, string> = {};
        err.fieldErrors.forEach((fe) => (map[fe.field] = fe.message));
        setFormErrors(map);
        setTopError(err.detail ?? null);
      } else {
        setTopError(
          err instanceof ApiError ? err.message : "Could not save the idea.",
        );
      }
    } finally {
      setSaving(false);
    }
  }

  async function handleVisibility(newVis: IdeaVisibility) {
    if (idea?.visibility === newVis) return;
    setSavingVisibility(true);
    setTopError(null);
    try {
      const updated = await api.setVisibility(params.id, newVis);
      setIdea(updated);
      setValues(ideaToForm(updated));
    } catch (err) {
      setTopError(
        err instanceof ApiError ? err.message : "Could not change visibility.",
      );
    } finally {
      setSavingVisibility(false);
    }
  }

  async function handleGenerate() {
    if (generationPending.current || assessment?.in_progress) return;
    generationPending.current = true;
    setAssessError(null);
    setGenerating(true);
    try {
      // The returned status already contains the result. Keep the page mounted
      // rather than reloading the idea and replacing it with a full-page spinner.
      setAssessment(await api.generateAssessment(params.id));
    } catch (err) {
      setAssessError(
        err instanceof ApiError ? err.message : "Assessment generation failed. Please try again.",
      );
    } finally {
      generationPending.current = false;
      setGenerating(false);
    }
  }

  async function handleDelete() {
    if (
      !confirm(
        "Delete this idea and all its assessments? This cannot be undone.",
      )
    )
      return;
    try {
      await api.deleteIdea(params.id);
      router.push("/ideas");
    } catch (err) {
      setTopError(
        err instanceof ApiError ? err.message : "Could not delete the idea.",
      );
    }
  }

  if (loading) return <Spinner label="Loading the idea…" />;
  if (summary && !error) return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-3xl font-semibold">{summary.name}</h1>
      <Alert kind="info" message="The owner has shared this summary with registered users. Detailed planning and assessments remain private." />
      <Card className="space-y-4 p-6">
        <p><strong>Industry:</strong> <IndustryLabel value={summary.industry} /></p>
        <p><strong>Stage:</strong> {STAGE_LABELS[summary.business_stage]}</p>
        <p><strong>Location:</strong> {summary.target_location || "Not specified"}</p>
        <p><strong>Intended customers:</strong> {summary.intended_customers || "Not specified"}</p>
      </Card>
      <Link href="/dashboard" className="text-brand-700 underline">Back to dashboard</Link>
    </div>
  );
  if (error || !idea)
    return (
      <div className="space-y-4">
        <ErrorState
          message={error ?? "Could not load the idea."}
          onRetry={loadIdea}
        />
        <Link
          href="/ideas"
          className="text-sm font-medium text-brand-700 hover:underline"
        >
          ← Back to ideas
        </Link>
      </div>
    );

  const isOwner = user?.id === idea.owner_id;
  const latestValid = assessment?.latest_valid;

  return (
    <div className="space-y-6">
      <div className="page-heading">
        <div>
          <h1 className="break-words text-3xl font-semibold tracking-tight text-navy">
            {idea.name}
          </h1>
          <p className="text-sm text-muted-light">
            <IndustryLabel value={idea.industry} /> ·{" "}
            {STAGE_LABELS[idea.business_stage]} · Revision{" "}
            {idea.revision_number}
          </p>
        </div>
        <Link
          href="/ideas"
          className="text-sm font-medium text-brand-700 hover:underline"
        >
          ← Back
        </Link>
      </div>

      {topError && <Alert message={topError} />}

      {/* Visibility setting (screen 12) */}
      {isOwner && (
        <Card className="p-4">
          <h2 className="text-sm font-semibold text-navy">
            Who can see this idea
          </h2>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {(Object.keys(VISIBILITY_LABELS) as IdeaVisibility[]).map((v) => (
              <button
                key={v}
                type="button"
                disabled={savingVisibility || editing || assessmentBusy}
                aria-pressed={idea.visibility === v}
                onClick={() => handleVisibility(v)}
                className={`rounded-md border px-3 py-1.5 text-sm ${
                  idea.visibility === v
                    ? "border-brand-500 bg-brand-50 text-brand-700"
                    : "border-navy/20 text-navy hover:bg-sand-100"
                } disabled:opacity-50`}
              >
                {VISIBILITY_LABELS[v]}
              </button>
            ))}
          </div>
        </Card>
      )}

      {/* Idea details / edit (screen 9) */}
      <Card className="p-5 sm:p-8">
        {isOwner && !editing ? (
          <div className="space-y-3">
            <div className="flex justify-end">
              <Button
                variant="secondary"
                disabled={assessmentBusy || savingVisibility}
                onClick={() => setEditing(true)}
              >
                Edit idea
              </Button>
            </div>
            <IdeaReadOnly idea={idea} />
          </div>
        ) : editing && values ? (
          <form onSubmit={handleSave} className="space-y-5">
            <h2 className="text-lg font-semibold text-navy">Edit idea</h2>
            <IdeaForm values={values} errors={formErrors} onChange={update} />
            <div className="flex justify-end gap-3">
              <Button
                type="button"
                variant="secondary"
                disabled={saving}
                onClick={() => {
                  setValues(ideaToForm(idea));
                  setFormErrors({});
                  setTopError(null);
                  setEditing(false);
                }}
              >
                Cancel
              </Button>
              <Button type="submit" loading={saving}>
                Save changes
              </Button>
              <Button type="button" loading={saving || generating} onClick={e => handleSave(e, true)}>
                Save and assess
              </Button>
            </div>
          </form>
        ) : (
          <IdeaReadOnly idea={idea} />
        )}
      </Card>

      {/* Assessment workspace + result (screens 10, 11) — owner only */}
      {isOwner && (
        <Card className="p-5 sm:p-8">
          <div className="page-heading">
            <h2 className="text-lg font-semibold text-navy">
              AI business assessment
            </h2>
            <Button
              onClick={handleGenerate}
              loading={assessmentBusy}
              disabled={
                assessmentBusy ||
                editing ||
                assessmentLoading ||
                !assessment
              }
            >
              {assessmentBusy
                ? "Generating…"
                : assessError || assessment?.current_status === "failed"
                  ? "Retry assessment"
                : latestValid
                  ? "Regenerate assessment"
                  : "Generate assessment"}
            </Button>
          </div>

          {assessError && !assessmentBusy && (
            <div className="mt-3">
              <Alert message={assessError} />
            </div>
          )}

          {assessError && !assessmentBusy && (
            <Button variant="ghost" className="mt-3" disabled={assessmentBusy} onClick={loadAssessment}>
              Retry assessment status
            </Button>
          )}
          {latestValid && latestValid.idea_revision !== idea.revision_number && <Alert kind="info" message="This assessment was generated for an earlier revision. Regenerate it to reflect your saved changes." />}
          {assessmentBusy && <AssessmentLoading />}
          <AssessmentPanel status={assessment} loading={assessmentLoading} generating={assessmentBusy} />
        </Card>
      )}

      {isOwner && <IdeaOpportunities key={`${idea.visibility}:${idea.revision_number}`} idea={idea} assessment={latestValid} />}

      {isOwner && (
        <div className="flex justify-end">
          <Button
            variant="danger"
            disabled={assessmentBusy || saving || savingVisibility}
            onClick={handleDelete}
          >
            Delete idea
          </Button>
        </div>
      )}
    </div>
  );
}

function IdeaReadOnly({ idea }: { idea: BusinessIdea }) {
  return (
    <dl className="grid gap-x-8 gap-y-6 sm:grid-cols-2">
      <Field label="Problem" value={idea.problem} full />
      <Field label="Solution" value={idea.solution} full />
      <div><dt className="text-xs font-medium uppercase text-muted-light">Industry</dt><dd className="text-sm"><IndustryLabel value={idea.industry} /></dd></div>
      <Field label="Industry specialisation" value={idea.industry_detail} />
      <Field label="Stage" value={STAGE_LABELS[idea.business_stage]} />
      <Field label="Target location" value={idea.target_location} />
      <Field label="Budget" value={idea.budget} />
      <Field label="Intended customers" value={idea.intended_customers} full />
      <Field label="Current challenges" value={idea.current_challenges} full />
      <Field label="Business model" value={idea.business_model} full />
      <Field label="Value proposition" value={idea.value_proposition} full />
      <Field label="Revenue model" value={idea.revenue_model} full />
      <Field label="Market opportunity and evidence" value={idea.market_opportunity} full />
      <Field label="Competition and alternatives" value={idea.competition} full />
      <Field label="Costs and operating requirements" value={idea.cost_structure} full />
      <Field label="Growth strategy" value={idea.growth_strategy} full />
      <Field label="Visibility" value={VISIBILITY_LABELS[idea.visibility]} />
    </dl>
  );
}

function Field({
  label,
  value,
  full,
}: {
  label: string;
  value: string;
  full?: boolean;
}) {
  return (
    <div className={full ? "sm:col-span-2" : ""}>
      <dt className="text-xs font-medium uppercase tracking-wide text-muted-light">
        {label}
      </dt>
      <dd className="mt-0.5 whitespace-pre-wrap text-sm text-navy">
        {value || "—"}
      </dd>
    </div>
  );
}

function AssessmentPanel({
  status,
  loading,
  generating,
}: {
  status: AssessmentStatusResponse | null;
  loading: boolean;
  generating: boolean;
}) {
  if (loading)
    return (
      <div className="mt-4">
        <Spinner label="Loading assessment…" />
      </div>
    );
  if (!status) return null;

  if (generating && !status.latest_valid) return null;

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
      {!generating && status.current_status === "failed" && status.error_message && (
        <Alert message={`Last attempt failed: ${status.error_message}`} />
      )}
      {status.latest_valid ? (
        <div key={status.latest_valid.id} className="assessment-result space-y-4">
          {generating && <p className="text-sm text-muted-light">Your previous assessment remains available while the new one is generated.</p>}
          <p className="text-sm font-medium text-brand-700">{status.latest_valid.provider === "gemini" ? "Gemini business-plan assessment" : status.latest_valid.provider === "mock" ? "Simulated demonstration assessment. Regenerate with Gemini for a real plan review." : "Earlier assessment: provider was not recorded."}</p>
          <p className="text-xs text-muted-light">
            Generated from idea revision {status.latest_valid.idea_revision}
          </p>
          <AssessmentSection
            title="Market considerations"
            text={status.latest_valid.market_considerations}
          />
          <AssessmentSection
            title="Target customers"
            text={status.latest_valid.target_customer_analysis}
          />
          <AssessmentSection
            title="Competitors"
            text={status.latest_valid.competitor_considerations}
          />
          <AssessmentSection
            title="Indicative costs"
            text={status.latest_valid.indicative_costs}
          />
          <AssessmentSection
            title="Suggested next steps"
            text={status.latest_valid.suggested_next_steps}
          />
          <AssessmentSection
            title="Assumptions"
            text={status.latest_valid.assumptions}
            highlight
          />
          <AssessmentSection
            title="Sources"
            text={status.latest_valid.sources}
          />
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
  // The Assumptions block uses the rare Warm Gold highlight so uncertain
  // information stands out clearly (guide §22: gold used sparingly).
  return (
    <div
      className={`rounded-md border p-4 ${
        highlight ? "border-gold-200 bg-gold-50" : "border-navy/10 bg-sand-50"
      }`}
    >
      <h3
        className={`text-sm font-semibold ${highlight ? "text-gold-700" : "text-navy"}`}
      >
        {title}
      </h3>
      <p className="mt-1 whitespace-pre-wrap text-sm text-navy">
        {text || "—"}
      </p>
    </div>
  );
}
