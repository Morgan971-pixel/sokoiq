import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SokoIQ — NSE Equity Research",
  description: "AI-powered investment briefs for Nairobi Securities Exchange companies",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-white antialiased">{children}</body>
    </html>
  );
}
