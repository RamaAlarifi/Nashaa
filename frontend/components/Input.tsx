"use client";

import { forwardRef, useId } from "react";

// Shared form controls. Labels use Deep Navy; focus uses Emerald (guide §22).
// Error states keep a distinct red so problems are clear without relying on
// color alone (each error also has an aria-message).

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
}

const FIELD_BASE =
  "form-control min-h-12 w-full rounded-xl border bg-white px-4 py-3 text-base text-navy placeholder:text-muted-light/70 outline-none focus:ring-2 disabled:bg-sand-100 disabled:cursor-not-allowed";

function errorClass(error?: string) {
  return error
    ? "border-red-400 focus:border-red-400 focus:ring-red-200"
    : "border-navy/15 focus:border-brand-500 focus:ring-brand-100";
}

function Label({
  htmlFor,
  children,
}: {
  htmlFor?: string;
  children: React.ReactNode;
}) {
  return (
    <label
      htmlFor={htmlFor}
      className="mb-1 block text-sm font-medium text-navy"
    >
      {children}
    </label>
  );
}

function Hint({ id, children }: { id?: string; children: React.ReactNode }) {
  return (
    <p id={id} className="mt-1 text-xs text-muted-light">
      {children}
    </p>
  );
}

function ErrorText({
  id,
  children,
}: {
  id?: string;
  children: React.ReactNode;
}) {
  return (
    <p id={id} className="mt-1 text-xs font-medium text-red-600" role="alert">
      {children}
    </p>
  );
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, error, hint, id, className = "", ...props },
  ref,
) {
  const generatedId = useId();
  const inputId = id || props.name || generatedId;
  return (
    <div className={className}>
      <Label htmlFor={inputId}>{label}</Label>
      <input
        ref={ref}
        id={inputId}
        aria-invalid={error ? "true" : undefined}
        aria-describedby={
          error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined
        }
        className={`${FIELD_BASE} ${errorClass(error)}`}
        {...props}
      />
      {hint && !error && <Hint id={`${inputId}-hint`}>{hint}</Hint>}
      {error && <ErrorText id={`${inputId}-error`}>{error}</ErrorText>}
    </div>
  );
});

interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  error?: string;
  hint?: string;
}

export const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(
  function TextArea({ label, error, hint, id, className = "", ...props }, ref) {
    const generatedId = useId();
    const inputId = id || props.name || generatedId;
    return (
      <div className={className}>
        <Label htmlFor={inputId}>{label}</Label>
        <textarea
          ref={ref}
          id={inputId}
          aria-invalid={error ? "true" : undefined}
          aria-describedby={
            error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined
          }
          className={`${FIELD_BASE} ${errorClass(error)}`}
          {...props}
        />
        {hint && !error && <Hint id={`${inputId}-hint`}>{hint}</Hint>}
        {error && <ErrorText id={`${inputId}-error`}>{error}</ErrorText>}
      </div>
    );
  },
);

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  error?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  function Select(
    { label, error, id, className = "", children, ...props },
    ref,
  ) {
    const generatedId = useId();
    const inputId = id || props.name || generatedId;
    return (
      <div className={className}>
        <Label htmlFor={inputId}>{label}</Label>
        <select
          ref={ref}
          id={inputId}
          aria-invalid={error ? "true" : undefined}
          aria-describedby={error ? `${inputId}-error` : undefined}
          className={`${FIELD_BASE} ${errorClass(error)}`}
          {...props}
        >
          {children}
        </select>
        {error && <ErrorText id={`${inputId}-error`}>{error}</ErrorText>}
      </div>
    );
  },
);
