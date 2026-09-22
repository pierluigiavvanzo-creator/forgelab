import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ForgeLab Control Plane",
  description: "Control Plane M8.1 per governare run, evidenze e decisioni ForgeLab.",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="it">
      <body className="antialiased">{children}</body>
    </html>
  );
}
