import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Data Insight AI",
  description: "AI-powered dataset analysis dashboard with charts, insights, and PDF reporting.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
