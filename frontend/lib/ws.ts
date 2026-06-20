import type { WsEvent } from "./types";

const WS_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(
  /^http/,
  "ws"
);

export function createResearchSocket(
  ticker: string,
  onEvent: (event: WsEvent) => void,
  onClose?: () => void
): WebSocket {
  const ws = new WebSocket(`${WS_BASE}/ws/research/${ticker}`);
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
