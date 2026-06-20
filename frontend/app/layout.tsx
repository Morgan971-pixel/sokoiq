import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "SokoIQ — NSE Equity Research",
  description: "AI-powered investment briefs for Nairobi Securities Exchange companies",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-white antialiased">
        <nav className="border-b border-gray-800 px-8 py-3 flex gap-6">
          <Link href="/" className="text-sm text-gray-400 hover:text-white transition-colors">
            Companies
          </Link>
          <Link href="/history" className="text-sm text-gray-400 hover:text-white transition-colors">
            History
          </Link>
        </nav>
        {children}
      </body>
    </html>
  );
}
