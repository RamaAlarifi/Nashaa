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
  menu: "M4 7h16 M4 12h16 M4 17h10",
  close: "M6 6l12 12 M18 6L6 18",
  chat: "M4 5h16v11H9l-5 4V5Z M8 10h8 M8 13h5",
  users: "M16 20v-1.5a4.5 4.5 0 0 0-9 0V20 M11.5 10a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z M17 4a3.5 3.5 0 0 1 0 6 M21 20v-1.5a4.5 4.5 0 0 0-3-4.2",
  shield: "M12 3 5 6v6c0 4.5 3 7.7 7 9 4-1.3 7-4.5 7-9V6l-7-3Z M9 12l2 2 4-4",
  file: "M14 3H6v18h12V7l-4-4Z M14 3v4h4 M9 13h6 M9 17h6",
  trend: "M3 17l6-6 4 4 8-8 M15 7h6v6",
  link: "M10 14a4 4 0 0 0 6 0l3-3a4 4 0 0 0-6-6l-1 1 M14 10a4 4 0 0 0-6 0l-3 3a4 4 0 0 0 6 6l1-1",
  bookmark: "M6 3h12v18l-6-4-6 4V3Z",
  flag: "M5 21V4 M5 4h11l-2 4 2 4H5",
  target: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z M12 12h.01",
  inbox: "M3 13h5l1 3h6l1-3h5 M5 5h14l2 8v6H3v-6l2-8Z",
} as const;

export type IconName = keyof typeof paths;

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
