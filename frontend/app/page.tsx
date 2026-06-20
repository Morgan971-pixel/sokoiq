import Link from "next/link";
import { getCompanies } from "@/lib/api";
import type { Company } from "@/lib/types";

export default async function Home() {
  let companies: Company[] = [];
  try {
    companies = await getCompanies();
  } catch {
    // backend not reachable at build time
  }

  return (
    <main className="min-h-screen p-8 max-w-4xl mx-auto">
      <div className="mb-10">
        <h1 className="text-4xl font-bold mb-2 tracking-tight">SokoIQ</h1>
        <p className="text-gray-400">
          AI-powered equity research for the Nairobi Securities Exchange
        </p>
      </div>

      {companies.length === 0 ? (
        <p className="text-gray-500 text-sm">
          Backend not reachable. Start the API server and refresh.
        </p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {companies.map((c) => (
            <Link
              key={c.ticker}
              href={`/research/${c.ticker}`}
              className="border border-gray-800 rounded-lg p-6 hover:border-green-500 hover:bg-gray-900 transition-colors"
            >
              <div className="text-green-400 font-mono text-sm mb-1">{c.ticker}</div>
              <div className="font-semibold text-white">{c.company_name}</div>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
