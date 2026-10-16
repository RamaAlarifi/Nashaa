"use client";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "./api";

interface Industry { id: string; label: string }
const IndustryContext = createContext<{ categories: Industry[]; loading: boolean; error: string; reload: () => Promise<void> }>({ categories: [], loading: true, error: "", reload: async () => {} });
export function IndustryProvider({ children }: { children: React.ReactNode }) {
  const [categories, setCategories] = useState<Industry[]>([]), [loading, setLoading] = useState(true), [error, setError] = useState("");
  const reload = useCallback(async () => {
    setLoading(true); setError("");
    try { setCategories(await api.opportunity<Industry[]>("/industries")); }
    catch (e) { setError(e instanceof Error ? e.message : "Industry categories could not be loaded."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void reload(); }, [reload]);
  return <IndustryContext.Provider value={{ categories, loading, error, reload }}>{children}</IndustryContext.Provider>;
}
export function useIndustries() {
  const context = useContext(IndustryContext);
  return { ...context, label: (value: string) => (context.categories.find(c => c.id === value)?.label ?? value) || "Not selected" };
}
export function IndustryLabel({ value }: { value: string }) { const { label } = useIndustries(); return <>{label(value)}</>; }
