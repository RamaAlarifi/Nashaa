// Shared surface primitive. The brand examples use clean, flat surfaces with
// subtle borders and shadows rather than heavy decoration (guide §22).
// Reuse this everywhere instead of repeating `rounded-lg border ... bg-white`.

import { forwardRef } from "react";

export const Card = forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(function Card({ className = "", children, ...props }, ref) {
  return (
    <div
      ref={ref}
      className={`surface ${className}`}
      {...props}
    >
      {children}
    </div>
  );
});
