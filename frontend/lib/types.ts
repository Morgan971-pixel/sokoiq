export interface Company {
  ticker: string;
  company_name: string;
}

export interface AgentStep {
  agent: string;
  status: "running" | "done" | "error";
  message: string;
  data?: Record<string, unknown>;
}

export interface InvestmentBrief {
  ticker: string;
  company_name: string;
  generated_at: string;
  recommendation: "BUY" | "HOLD" | "SELL" | "NEUTRAL";
  confidence: number;
  thesis: string;
  financials_summary: string;
  market_summary: string;
  news_summary: string;
  key_risks: string[];
  citations: string[];
}

export type WsEvent =
  | { type: "step"; data: AgentStep }
  | { type: "brief"; data: InvestmentBrief }
  | { type: "error"; data: { message: string } };

export interface BriefSummary {
  id: string;
  ticker: string;
  company_name: string;
  recommendation: "BUY" | "HOLD" | "SELL" | "NEUTRAL";
  confidence: number;
  thesis: string;
  generated_at: string;
}
