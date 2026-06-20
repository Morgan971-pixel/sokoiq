import type { WsEvent } from "./types";

const WS_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(
  /^http/,
  "ws"
);

export function createResearchSocket(
  ticker: string,
  onEvent: (event: WsEvent) => void,
  onClose?: () => void,
  demo = false
): WebSocket {
  const url = `${WS_BASE}/ws/research/${ticker}${demo ? "?demo=true" : ""}`;
  const ws = new WebSocket(url);
  ws.onmessage = (e) => {
    try {
      const event = JSON.parse(e.data as string) as WsEvent;
      onEvent(event);
    } catch {
      // ignore malformed frames
    }
  };
  ws.onclose = () => onClose?.();
  return ws;
}
