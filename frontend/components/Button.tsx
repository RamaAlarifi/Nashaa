"use client";

import { forwardRef } from "react";
import Link from "next/link";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost" | "gold";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
}

// Variants map to the official palette (guide §22):
//   primary   — Emerald, main actions
//   secondary — Deep Navy outline, neutral actions
//   danger    — destructive actions (kept distinct from brand)
//   ghost     — low-emphasis in-card actions
//   gold      — RESERVED for rare opportunity/investment highlights
const VARIANT_CLASSES: Record<ButtonVariant, string> = {
  primary:
    "button-primary bg-brand-600 text-white hover:bg-brand-700 disabled:bg-brand-300 disabled:shadow-none",
  secondary:
    "border border-navy/15 bg-white text-navy shadow-[0_1px_2px_#132a3a0d] hover:border-navy/30 hover:bg-sand-50 disabled:opacity-50",
  danger:
    "border border-red-200 bg-white text-red-700 hover:border-red-300 hover:bg-red-50 disabled:opacity-50",
  ghost: "text-brand-700 hover:bg-brand-50 disabled:opacity-50",
  gold: "bg-gold-500 text-navy shadow-[inset_0_1px_0_#ffffff40,0_4px_12px_-4px_#d4a63880] hover:bg-gold-600 disabled:opacity-60",
};

const SIZE_CLASSES: Record<ButtonSize, string> = {
  sm: "min-h-9 px-3.5 py-1.5 text-[0.8125rem]",
  md: "min-h-11 px-5 py-2.5 text-sm",
  lg: "min-h-12 px-6 py-3 text-[0.9375rem]",
};

export function buttonClasses(
  variant: ButtonVariant = "primary",
  size: ButtonSize = "md",
  className = "",
) {
  return `button inline-flex shrink-0 items-center justify-center gap-2 rounded-xl font-medium tracking-[-0.005em] disabled:cursor-not-allowed ${SIZE_CLASSES[size]} ${VARIANT_CLASSES[variant]} ${className}`;
}

export function ButtonLink({
  variant = "primary",
  size = "md",
  className = "",
  ...props
}: React.ComponentProps<typeof Link> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
}) {
  return (
    <Link className={buttonClasses(variant, size, className)} {...props} />
  );
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  function Button(
    {
      variant = "primary",
      size = "md",
      loading = false,
      disabled,
      className = "",
      children,
      ...props
    },
    ref,
  ) {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        aria-busy={loading || undefined}
        className={buttonClasses(variant, size, className)}
        {...props}
      >
        {loading && (
          <span
            className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
            aria-hidden="true"
          />
        )}
        {children}
      </button>
    );
  },
);
