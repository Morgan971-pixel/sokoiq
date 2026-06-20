"use client";

import type { InvestmentBrief } from "@/lib/types";

const REC_COLOR: Record<string, string> = {
  BUY: "text-green-400 border-green-400",
  HOLD: "text-yellow-400 border-yellow-400",
  SELL: "text-red-400 border-red-400",
  NEUTRAL: "text-gray-400 border-gray-400",
};

export function BriefPanel({ brief }: { brief: InvestmentBrief }) {
  return (
    <div className="space-y-5">
      <div className="flex items-center gap-4">
        <span
          className={`text-3xl font-bold border-2 px-3 py-1 rounded tracking-wide ${REC_COLOR[brief.recommendation]}`}
        >
          {brief.recommendation}
        </span>
        <div className="text-sm text-gray-400">
          <div>Confidence: {(brief.confidence * 100).toFixed(0)}%</div>
          <div className="text-xs">{brief.generated_at.replace("T", " ").replace("Z", " UTC")}</div>
        </div>
      </div>

      <p className="text-gray-200 leading-relaxed">{brief.thesis}</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div>
          <h4 className="text-gray-400 font-semibold mb-1 uppercase text-xs tracking-wide">Financials</h4>
          <p className="text-gray-300">{brief.financials_summary}</p>
        </div>
        <div>
          <h4 className="text-gray-400 font-semibold mb-1 uppercase text-xs tracking-wide">Market</h4>
          <p className="text-gray-300">{brief.market_summary}</p>
        </div>
        <div>
          <h4 className="text-gray-400 font-semibold mb-1 uppercase text-xs tracking-wide">News</h4>
          <p className="text-gray-300">{brief.news_summary}</p>
        </div>
      </div>

      {brief.key_risks.length > 0 && (
        <div>
          <h4 className="text-gray-400 font-semibold mb-2 uppercase text-xs tracking-wide">Key Risks</h4>
          <ul className="list-disc list-inside text-red-300 text-sm space-y-1">
            {brief.key_risks.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}

      {brief.citations.length > 0 && (
        <div className="text-xs text-gray-600 pt-2 border-t border-gray-800">
          Sources: {brief.citations.join(", ")}
        </div>
      )}
    </div>
  );
}
