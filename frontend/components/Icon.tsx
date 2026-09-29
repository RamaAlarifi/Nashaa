import type { SVGProps } from "react";

const paths = {
  grid: "M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",
  idea: "M9 18h6 M9 21h6 M8 14a7 7 0 1 1 8 0c-1 1-1 2-1 2H9s0-1-1-2Z",
  user: "M20 21v-2a7 7 0 0 0-14 0v2 M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z",
  arrow: "M5 12h14 M13 6l6 6-6 6",
  plus: "M12 5v14 M5 12h14",
  spark: "m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z",
  check: "m5 12 4 4L19 6",
  search: "M21 21l-5-5 M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z",
  lock: "M6 10h12v11H6z M8 10V6a4 4 0 0 1 8 0v4",
  logout: "M9 4H4v16h5 M9 12h12 M16 7l5 5-5 5",
} as const;

export function Icon({
  name,
  className = "h-5 w-5",
  ...props
}: SVGProps<SVGSVGElement> & { name: keyof typeof paths }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className}
      {...props}
    >
      <path d={paths[name]} />
    </svg>
  );
}
