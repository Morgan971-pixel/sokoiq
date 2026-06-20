from collections import defaultdict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, ws: WebSocket, room: str) -> None:
        await ws.accept()
        self.active[room].append(ws)

    def disconnect(self, ws: WebSocket, room: str) -> None:
        self.active[room] = [c for c in self.active[room] if c is not ws]

    async def broadcast(self, message: dict, room: str) -> None:
        dead: list[WebSocket] = []
        for ws in list(self.active[room]):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, room)


manager = ConnectionManager()
