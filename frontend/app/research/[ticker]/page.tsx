"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { AgentFeed } from "@/components/AgentFeed";
import { BriefPanel } from "@/components/BriefPanel";
import { createResearchSocket } from "@/lib/ws";
import type { AgentStep, InvestmentBrief, WsEvent } from "@/lib/types";

export default function ResearchPage() {
  const { ticker } = useParams<{ ticker: string }>();
  const searchParams = useSearchParams();
  const demo = searchParams.get("demo") === "true";
  const [steps, setSteps] = useState<AgentStep[]>([]);
  const [brief, setBrief] = useState<InvestmentBrief | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const startResearch = () => {
    setSteps([]);
    setBrief(null);
    setError(null);
    setRunning(true);
    wsRef.current?.close();

    wsRef.current = createResearchSocket(
      ticker,
      (event: WsEvent) => {
        if (event.type === "step") {
          setSteps((prev) => [...prev, event.data]);
        } else if (event.type === "brief") {
          setBrief(event.data);
          setRunning(false);
        } else if (event.type === "error") {
          setError(event.data.message);
          setRunning(false);
        }
      },
      () => setRunning(false),
      demo
    );
  };

  useEffect(() => {
    return () => wsRef.current?.close();
  }, []);

  return (
    <main className="min-h-screen p-8 max-w-4xl mx-auto">
      <a
        href="/"
        className="text-gray-500 text-sm mb-6 block hover:text-gray-300 transition-colors"
      >
        Back to companies
      </a>

      <div className="flex items-start gap-4 mb-8">
        <div>
          <div className="text-green-400 font-mono text-lg">{ticker?.toUpperCase()}</div>
          <h1 className="text-3xl font-bold">Research Brief</h1>
        </div>
        <button
          onClick={startResearch}
          disabled={running}
          className="ml-auto bg-green-600 hover:bg-green-500 disabled:bg-gray-700 disabled:cursor-not-allowed px-6 py-3 rounded-lg font-semibold transition-colors"
        >
          {running ? "Researching..." : "Run Research"}
        </button>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 mb-6 text-red-300 text-sm">
          {error}
        </div>
      )}

      {steps.length > 0 && (
        <div className="bg-gray-900 rounded-lg p-6 mb-6">
          <h2 className="text-gray-400 text-xs font-semibold mb-4 uppercase tracking-widest">
            Agent Activity
          </h2>
          <AgentFeed steps={steps} />
        </div>
      )}

      {brief && (
        <div className="bg-gray-900 rounded-lg p-6">
          <h2 className="text-gray-400 text-xs font-semibold mb-4 uppercase tracking-widest">
            Investment Brief
          </h2>
          <BriefPanel brief={brief} />
        </div>
      )}
    </main>
  );
}
