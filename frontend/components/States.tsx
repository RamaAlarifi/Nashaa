// Reusable state components: loading, empty, error, and an alert banner.
// These satisfy the "useful error, loading, and empty states" screen (13) and
// stay aligned with the brand palette (guide §22).

export function Spinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div
      className="flex flex-col items-center justify-center gap-4 py-16 text-muted-light"
      role="status"
    >
      <span className="relative flex h-10 w-10 items-center justify-center">
        <span className="absolute inset-0 rounded-full border-2 border-brand-500/15" />
        <span className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-brand-500" />
        <span className="h-1.5 w-1.5 rounded-full bg-turquoise-500" />
      </span>
      <span className="text-sm">{label}</span>
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-dashed border-navy/15 bg-white/70 px-6 py-14 text-center">
      <span
        className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-500/10"
        aria-hidden="true"
      >
        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
          <path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z" />
        </svg>
      </span>
      <p className="text-base font-semibold text-navy">{title}</p>
      {description && (
        <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-muted-light">{description}</p>
      )}
      {action && <div className="mt-6 flex justify-center">{action}</div>}
    </div>
  );
}

export function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
}: {
  title?: string;
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div
      className="mx-auto max-w-lg rounded-2xl border border-red-200 bg-white p-8 text-center shadow-[0_1px_2px_#132a3a0a]"
      role="alert"
    >
      <span className="mx-auto mb-4 flex h-11 w-11 items-center justify-center rounded-full bg-red-50 text-lg font-semibold text-red-600" aria-hidden="true">
        !
      </span>
      <p className="font-semibold text-navy">{title}</p>
      <p className="mt-2 text-sm leading-relaxed text-red-700">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="button mt-5 inline-flex min-h-10 items-center rounded-xl border border-red-200 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function Alert({
  kind = "error",
  message,
}: {
  kind?: "error" | "success" | "info";
  message: string;
}) {
  const styles = {
    error: "border-red-200 bg-red-50/80 text-red-700",
    success: "border-brand-200 bg-brand-50 text-brand-700",
    info: "border-turquoise-100 bg-turquoise-50 text-turquoise-700",
  }[kind];
  const dot = {
    error: "bg-red-500",
    success: "bg-brand-500",
    info: "bg-turquoise-500",
  }[kind];
  return (
    <div
      className={`page-enter flex items-start gap-3 rounded-xl border px-4 py-3 text-sm leading-relaxed ${styles}`}
      role={kind === "error" ? "alert" : "status"}
    >
      <span className={`mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full ${dot}`} aria-hidden="true" />
      <span className="min-w-0">{message}</span>
    </div>
  );
}
