/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Nashaa brand palette (derived from the project branding).
        brand: {
          50: "#f0f9f4",
          100: "#dcf0e3",
          200: "#bbe1ca",
          300: "#8acaa6",
          400: "#54ad7d",
          500: "#329060",
          600: "#23734c",
          700: "#1c5b3e",
          800: "#184833",
          900: "#143b2b",
        },
      },
      fontFamily: {
        sans: ["system-ui", "Segoe UI", "Tahoma", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
};
