"use client";
import { Select } from "./Input";
import { useIndustries } from "@/lib/industries";

type Props = React.ComponentProps<typeof Select>;
export function IndustrySelect({ value, defaultValue, children, ...props }: Props) {
  const { categories, loading, error, reload } = useIndustries();
  const selected = String(value ?? defaultValue ?? "");
  return <div><Select key={loading ? "loading" : "ready"} {...props} value={value} defaultValue={defaultValue} disabled={props.disabled || loading}>
    <option value="">{loading ? "Loading industries…" : "Not selected"}</option>
    {selected && !categories.some(c => c.id === selected) && <option value={selected}>Previously entered: {selected}</option>}
    {categories.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}{children}
  </Select>{error && <p role="alert" className="mt-2 text-sm text-red-700">{error} <button type="button" className="underline" onClick={reload}>Retry categories</button></p>}</div>;
}
export function IndustryMultiSelect({ selected, ...props }: Omit<Props, "value" | "defaultValue" | "multiple"> & { selected: string[] }) {
  const { categories, loading, error } = useIndustries();
  return <div><Select key={loading ? "loading" : "ready"} {...props} multiple size={5} defaultValue={selected} disabled={props.disabled || loading}>
    {selected.filter(value => !categories.some(c => c.id === value)).map(value => <option key={value} value={value}>Previously entered: {value}</option>)}
    {categories.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
  </Select><p className="mt-1 text-xs text-muted-light">Select one or more industries. Use Ctrl or Command to select multiple categories.</p>{error && <p role="alert" className="text-sm text-red-700">{error}</p>}</div>;
}
