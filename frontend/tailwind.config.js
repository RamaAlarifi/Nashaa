/** @type {import('tailwindcss').Config} */
// Nashaa official identity (see docs/interface-guide.md and Nashaa_Guide.md §22).
// Emerald is the primary; Deep Navy is for text/navigation/dark surfaces;
// Turquoise is a small AI/tech accent; Warm Gold is reserved for rare
// opportunity/investment highlights; Soft Sand is the default page background.
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary brand color (Emerald #087F5B). The `brand.*` scale is anchored
        // on the official value so existing `bg-brand-600` etc. use the real
        // palette without renaming every class.
        brand: {
          50: "#E6F4EE",
          100: "#C9E6D7",
          200: "#A8D9C4",
          300: "#6BBA97",
          400: "#2E9D75",
          500: "#087F5B", // official Emerald
          600: "#087F5B", // primary actions (alias of 500)
          700: "#066A4D", // hover / active
          800: "#054D38",
          900: "#043A2B",
        },
        // Deep Navy #132A3A — brand name, main text, navigation, dark surfaces.
        navy: {
          DEFAULT: "#132A3A",
          50: "#E7EBEE",
          100: "#C8D0D4",
          600: "#1B3A4F",
          700: "#173041",
          800: "#0E2230",
          900: "#0A1A26",
        },
        // Turquoise #20BFA9 — small technology / AI accent, icon on dark.
        turquoise: {
          50: "#E3F8F4",
          100: "#BEEFE8",
          400: "#4FCBBC",
          500: "#20BFA9",
          600: "#1AA894",
          700: "#116B60",
        },
        // Warm Gold #E9B949 — rare opportunity / investment accent only.
        gold: {
          50: "#FBF1D6",
          100: "#F6E2AE",
          200: "#EFCE7C",
          500: "#E9B949",
          600: "#D4A638",
          700: "#806014",
        },
        // Soft Sand #F7F5EF — default light page background & quiet surfaces.
        sand: {
          DEFAULT: "#F7F5EF",
          50: "#FAF9F6",
          100: "#F0EDE3",
          200: "#E9E5D7",
        },
        // Tagline / muted text.
        muted: {
          light: "#4E5F6B", // on light backgrounds
          dark: "#C8D0D4", // on dark backgrounds
        },
      },
      fontFamily: {
        // English interface text — Poppins (loaded in app/layout.tsx via next/font).
        sans: [
          "var(--font-poppins)",
          "Poppins",
          "system-ui",
          "Segoe UI",
          "Tahoma",
          "Arial",
          "sans-serif",
        ],
        // Arabic interface text — Alexandria (or IBM Plex Sans Arabic fallback).
        arabic: [
          "Alexandria",
          "IBM Plex Sans Arabic",
          "system-ui",
          "sans-serif",
        ],
      },
      borderRadius: {
        // Consistent radii used across cards, buttons, inputs.
        DEFAULT: "0.5rem", // 8px — inputs, buttons
        lg: "0.75rem", // 12px — cards
        xl: "0.875rem", // 14px — prominent cards / auth panels
      },
      boxShadow: {
        // Subtle, flat surfaces — the brand examples avoid heavy decoration.
        card: "0 1px 2px rgba(19, 42, 58, 0.06), 0 1px 3px rgba(19, 42, 58, 0.04)",
        elevated: "0 4px 14px rgba(19, 42, 58, 0.08)",
      },
      maxWidth: {
        // App content width used by AppShell.
        app: "72rem",
      },
      spacing: {
        // Documented spacing scale (see docs/interface-guide.md).
        18: "4.5rem",
      },
    },
  },
  plugins: [],
};
