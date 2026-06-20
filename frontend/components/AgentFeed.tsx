"use client";

import type { AgentStep } from "@/lib/types";

const AGENT_LABELS: Record<string, string> = {
  filing_analyst: "Filing Analyst",
  market_analyst: "Market Analyst",
  news_analyst: "News Analyst",
  memo_writer: "Memo Writer",
};

const STATUS_COLOR: Record<string, string> = {
  running: "text-yellow-400",
  done: "text-green-400",
  error: "text-red-400",
};

const STATUS_ICON: Record<string, string> = {
  running: "...",
  done: "OK",
  error: "ERR",
};

export function AgentFeed({ steps }: { steps: AgentStep[] }) {
  if (steps.length === 0) return null;

  return (
    <div className="space-y-2 font-mono text-sm">
      {steps.map((step, i) => (
        <div key={i} className="flex gap-3 items-start">
          <span className={`w-4 shrink-0 text-xs pt-0.5 ${STATUS_COLOR[step.status]}`}>
            {STATUS_ICON[step.status]}
          </span>
          <span className={`font-semibold w-36 shrink-0 ${STATUS_COLOR[step.status]}`}>
            {AGENT_LABELS[step.agent] ?? step.agent}
          </span>
          <span className="text-gray-300 break-words">{step.message}</span>
        </div>
      ))}
    </div>
  );
}
