"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { Input, Select, TextArea } from "./Input";
import { Button } from "./Button";
import { Alert, Spinner } from "./States";
import { Card } from "./Card";
import { IndustrySelect, IndustryMultiSelect } from "./IndustrySelect";
import type { Match } from "@/lib/opportunity-types";

export function useResource<T>(path: string | null) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const generation = useRef(0);
  const reload = useCallback(async () => {
    const current = ++generation.current;
    if (!path) { setData(null); setLoading(false); return; }
    setLoading(true); setError("");
    try { const value = await api.opportunity<T>(path); if (current === generation.current) setData(value); }
    catch (e) { if (current === generation.current) { setData(null); setError(e instanceof Error ? e.message : "Could not load this page."); } }
    finally { if (current === generation.current) setLoading(false); }
  }, [path]);
  useEffect(() => { void reload(); }, [reload]);
  return { data, error, loading, reload };
}

export function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return <Card className="space-y-5 p-5 sm:p-7"><h2 className="text-lg font-semibold text-navy">{title}</h2>{children}</Card>;
}

export function LoadState({ loading, error, retry }: { loading: boolean; error: string; retry: () => Promise<void> }) {
  if (loading) return <Spinner label="Loading your workspace…" />;
  if (error) return <div className="space-y-3"><Alert message={error} /><Button onClick={retry}>Try again</Button></div>;
  return null;
}

export interface Field {
  name: string; label: string; value?: string; type?: string; required?: boolean;
  options?: { value: string; label: string }[]; hint?: string; maxLength?: number;
}

export function ActionForm({ fields, label, submit, done, resetOnSuccess = false }: {
  fields: Field[]; label: string;
  submit: (values: Record<string, string>) => Promise<unknown>;
  done?: () => Promise<void> | void;
  resetOnSuccess?: boolean;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  return <form className="space-y-4" onSubmit={async e => {
    e.preventDefault(); const form = e.currentTarget;
    const formData = new FormData(form);
    const values = Object.fromEntries(formData.entries()) as Record<string, string>;
    fields.filter(f => f.type === "industries").forEach(f => { values[f.name] = formData.getAll(f.name).map(String).join(","); });
    setBusy(true); setError(""); setSuccess(false); setErrors({});
    try { await submit(values); if (resetOnSuccess) form.reset(); setSuccess(true); await done?.(); }
    catch (err) {
      setError(err instanceof ApiError ? err.fieldErrors?.map(x => x.message).join(" ") || err.message : err instanceof Error ? err.message : "The action could not be completed.");
      if (err instanceof ApiError) setErrors(Object.fromEntries((err.fieldErrors ?? []).map(x => [x.field.split(".")[0], x.message])));
    } finally { setBusy(false); }
  }}>
    {fields.map(f => {
      const props = { name: f.name, label: f.label, defaultValue: f.value ?? "", required: f.required ?? true, error: errors[f.name] };
      if (f.type === "industry") return <IndustrySelect key={f.name} {...props} />;
      if (f.type === "industries") return <IndustryMultiSelect key={f.name} name={f.name} label={f.label} required={f.required ?? true} error={errors[f.name]} selected={(f.value ?? "").split(",").map(v => v.trim()).filter(Boolean)} />;
      if (f.options) return <Select key={f.name} {...props}>{f.options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}</Select>;
      if (f.type === "textarea") return <TextArea key={f.name} {...props} hint={f.hint} maxLength={f.maxLength ?? 10000} rows={4} />;
      return <Input key={f.name} {...props} hint={f.hint} maxLength={f.maxLength ?? 200} type={f.type ?? "text"} min={f.type === "number" ? "0" : undefined} step={f.type === "number" ? "0.01" : undefined} />;
    })}
    {error && <Alert message={error} />}
    {success && <Alert kind="success" message="Saved successfully." />}
    <Button type="submit" loading={busy}>{label}</Button>
  </form>;
}

export function Action({ children, run, danger = false }: { children: React.ReactNode; run: () => Promise<unknown>; danger?: boolean }) {
  const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  return <div><Button variant={danger ? "danger" : "secondary"} loading={busy} onClick={async () => {
    setBusy(true); setError("");
    try { await run(); } catch (e) { setError(e instanceof Error ? e.message : "The action could not be completed."); }
    finally { setBusy(false); }
  }}>{children}</Button>{error && <p role="alert" className="mt-2 text-sm text-red-700">{error}</p>}</div>;
}

export function MatchDetails({ match }: { match: Match }) {
  return <div className="space-y-2 text-sm"><p className="font-medium text-brand-700">Compatibility: {match.score}% · available factors: {match.coverage}/100</p>
    <p>{match.reasons.join(" · ")}</p>{match.mismatches.map(x => <p key={x}>{x}</p>)}
    {match.missing.map(x => <p className="text-muted-light" key={x}>{x}</p>)}
    {!!match.history_sources.length && <p>History sources: {match.history_sources.join("; ")}</p>}
  </div>;
}

export const splitList = (value: string) => [...new Set(value.split(",").map(x => x.trim()).filter(Boolean))];
export const stageOptions = ["idea", "validation", "early", "operating", "scaling"].map(value => ({ value, label: value[0].toUpperCase() + value.slice(1) }));
