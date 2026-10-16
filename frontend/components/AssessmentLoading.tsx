"use client";

import { useEffect, useState } from "react";

// These are review topics, not measured backend stages. One Gemini request
// produces the complete assessment; no external research is performed.
const MESSAGES = [
  "Generating your business-plan assessment...",
  "The review considers your business model and customers.",
  "The review considers risks, assumptions and practical next steps.",
  "Still generating your assessment. You can continue browsing.",
];

export function AssessmentLoading() {
  const [message, setMessage] = useState(0);
  useEffect(() => {
    const timer = window.setInterval(() => {
      setMessage(current => Math.min(current + 1, MESSAGES.length - 1));
    }, 5000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="assessment-loading mt-5 rounded-2xl border border-brand-200 bg-brand-50/60 p-5 sm:p-6">
      <div className="flex items-start gap-4">
        <div className="relative flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white text-brand-700" aria-hidden="true">
          <span className="assessment-orbit absolute inset-0 rounded-2xl border-2 border-brand-200 border-t-brand-600" />
          <svg width="22" height="24" viewBox="0 0 22 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M5 2h8l5 5v15H4V2h1Zm8 0v6h5M7 12h8M7 16h8" />
          </svg>
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-navy">Your assessment is being generated</p>
          <p key={message} role="status" aria-live="polite" aria-atomic="true" className="assessment-message mt-1 min-h-10 text-sm text-brand-700">{MESSAGES[message]}</p>
          <p className="mt-2 text-xs leading-relaxed text-muted-light">Based on your submitted plan. No external research or verification is performed. Results will appear here as soon as they are ready.</p>
        </div>
      </div>
      <div className="mt-5 h-1.5 overflow-hidden rounded-full bg-brand-100" aria-hidden="true">
        <div className="assessment-sweep h-full w-1/3 rounded-full bg-gradient-to-r from-brand-300 via-brand-600 to-brand-300" />
      </div>
    </div>
  );
}
