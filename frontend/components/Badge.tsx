// Status badge primitive. Never rely on color alone to communicate status
// (guide §22 "interface application"); pair color with a text label.

type BadgeTone = "neutral" | "success" | "warn" | "danger" | "info" | "gold";

const TONES: Record<BadgeTone, string> = {
  neutral: "bg-navy-50 text-navy",
  success: "bg-brand-100 text-brand-700",
  warn: "bg-gold-50 text-gold-700",
  danger: "bg-red-100 text-red-700",
  info: "bg-turquoise-50 text-turquoise-700",
  gold: "bg-gold-100 text-gold-700",
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
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${TONES[tone]} ${className}`}
    >
      {children}
    </span>
  );
}
