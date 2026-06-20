import Link from "next/link";
import { getHistory } from "@/lib/api";
import type { BriefSummary } from "@/lib/types";

const REC_COLORS: Record<string, string> = {
  BUY:     "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
  HOLD:    "bg-amber-500/20  text-amber-400  border border-amber-500/30",
  SELL:    "bg-red-500/20    text-red-400    border border-red-500/30",
  NEUTRAL: "bg-gray-500/20   text-gray-400   border border-gray-500/30",
};

export default async function HistoryPage() {
  let briefs: BriefSummary[] = [];
  try {
    briefs = await getHistory();
  } catch {
    // backend not running
  }

  return (
    <main className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-8">Research History</h1>

        {briefs.length === 0 ? (
          <p className="text-gray-500 text-sm">
            No briefs generated yet. Run research on a company to see results here.
          </p>
        ) : (
          <div className="space-y-3">
            {briefs.map((b) => (
              <Link key={b.id} href={`/research/${b.ticker}`} className="block group">
                <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 group-hover:border-gray-600 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono font-bold bg-gray-800 text-gray-300 px-2 py-1 rounded">
                        {b.ticker}
                      </span>
                      <span className="text-white font-medium">{b.company_name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`text-xs font-bold px-2 py-1 rounded ${REC_COLORS[b.recommendation] ?? REC_COLORS.NEUTRAL}`}>
                        {b.recommendation}
                      </span>
                      <span className="text-gray-400 text-sm">
                        {Math.round(b.confidence * 100)}%
                      </span>
                      <span className="text-gray-600 text-xs">
                        {new Date(b.generated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-500 text-sm mt-2 line-clamp-2">{b.thesis}</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
