import type { BriefSummary, Company } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getCompanies(): Promise<Company[]> {
  const res = await fetch(`${API_BASE}/companies`);
  if (!res.ok) throw new Error(`Failed to fetch companies: ${res.status}`);
  return res.json();
}

export async function getHistory(ticker?: string): Promise<BriefSummary[]> {
  const params = ticker ? `?ticker=${encodeURIComponent(ticker)}` : "";
  const res = await fetch(`${API_BASE}/history${params}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch history: ${res.status}`);
  return res.json();
}
