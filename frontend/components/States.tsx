// Reusable state components: loading, empty, error, and an alert banner.
// These satisfy the "useful error, loading, and empty states" screen (13) and
// stay aligned with the brand palette (guide §22).

export function Spinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div
      className="flex items-center justify-center gap-3 py-8 text-muted-light"
      role="status"
    >
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
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
    <div className="rounded-2xl border border-dashed border-navy/15 bg-white px-6 py-12 text-center">
      <p className="font-medium text-navy">{title}</p>
      {description && (
        <p className="mt-1 text-sm text-muted-light">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
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
      className="rounded-lg border border-red-200 bg-red-50 p-6 text-center"
      role="alert"
    >
      <p className="font-medium text-red-700">{title}</p>
      <p className="mt-1 text-sm text-red-600">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 rounded-md border border-red-300 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100"
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
    error: "border-red-200 bg-red-50 text-red-700",
    success: "border-brand-200 bg-brand-50 text-brand-700",
    info: "border-turquoise-100 bg-turquoise-50 text-turquoise-700",
  }[kind];
  return (
    <div
      className={`rounded-md border px-4 py-3 text-sm ${styles}`}
      role={kind === "error" ? "alert" : "status"}
    >
      {message}
    </div>
  );
}
