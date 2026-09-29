import type { Metadata, Viewport } from "next";
import { Poppins } from "next/font/google";

import { AppShell } from "@/components/AppShell";
import { AuthProvider } from "@/lib/auth-context";

import "./globals.css";

// English interface font (Nashaa_Guide.md §22: Poppins for English interface text).
const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Nashaa — From Idea to Opportunity",
    template: "%s · Nashaa",
  },
  description:
    "Nashaa helps Saudi entrepreneurs and small businesses move from a business idea to practical action.",
  applicationName: "Nashaa",
  icons: {
    icon: [{ url: "/brand/favicon.svg", type: "image/svg+xml" }],
    apple: [{ url: "/brand/icon.svg", type: "image/svg+xml" }],
  },
};

export const viewport: Viewport = {
  themeColor: "#087F5B",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={poppins.variable}>
      <body>
        <AuthProvider>
          <AppShell>{children}</AppShell>
        </AuthProvider>
      </body>
    </html>
  );
}
