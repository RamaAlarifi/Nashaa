// Unmodified official outlined artwork. Never recreate the custom wordmark.
type LogoVariant = "default" | "reversed";
export function LogoMark({ variant = "default", className = "", title = "Nashaa" }: {
  variant?: LogoVariant; className?: string; title?: string;
}) {
  return <img src={variant === "reversed" ? "/brand/logo-mark-reversed.svg" : "/brand/logo-mark.svg"}
    alt={title} className={`min-h-6 min-w-6 ${className}`} width={32} height={32} />;
}
export function Logo({ variant = "default", showWordmark = true, showTagline = false, className = "", markClassName = "" }: {
  variant?: LogoVariant; showWordmark?: boolean; showTagline?: boolean; className?: string; markClassName?: string;
}) {
  if (!showWordmark) return <span className={`inline-flex p-4 ${className}`}><LogoMark variant={variant} className={markClassName || "h-8 w-8"} /></span>;
  const reversed = variant === "reversed" ? "-reversed" : "";
  return <span className={`inline-flex p-4 ${className}`}>
    <img src={`/brand/logo${showTagline ? "-tagline" : ""}${reversed}.svg`}
      alt={showTagline ? "Nashaa — From Idea to Opportunity" : "Nashaa | نشأة"}
      className={showTagline ? "h-auto w-[240px] min-w-[240px]" : "h-auto w-[152px] min-w-[120px]"} />
  </span>;
}
