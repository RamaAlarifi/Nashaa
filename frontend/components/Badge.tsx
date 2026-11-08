// Status badge primitive. Never rely on color alone to communicate status
// (guide §22 "interface application"); pair color with a text label.

type BadgeTone = "neutral" | "success" | "warn" | "danger" | "info" | "gold";

const TONES: Record<BadgeTone, string> = {
  neutral: "bg-navy-50/80 text-navy ring-navy/10",
  success: "bg-brand-50 text-brand-700 ring-brand-500/20",
  warn: "bg-gold-50 text-gold-700 ring-gold-500/30",
  danger: "bg-red-50 text-red-700 ring-red-600/15",
  info: "bg-turquoise-50 text-turquoise-700 ring-turquoise-500/25",
  gold: "bg-gold-100 text-gold-700 ring-gold-500/30",
};

export function Badge({
  tone = "neutral",
  className = "",
  children,
}: {
  tone?: BadgeTone;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${TONES[tone]} ${className}`}
    >
      {children}
    </span>
  );
}
