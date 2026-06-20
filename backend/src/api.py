from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.graph import run_research_pipeline
from src.models import COMPANIES, TICKER_MAP
from src.ws_manager import manager

app = FastAPI(title="SokoIQ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/companies")
async def list_companies():
    return [c.model_dump() for c in COMPANIES]


@app.websocket("/ws/research/{ticker}")
async def research_ws(websocket: WebSocket, ticker: str) -> None:
    ticker = ticker.upper()
    if ticker not in TICKER_MAP:
        await websocket.close(code=4004)
        return

    company_name = TICKER_MAP[ticker]
    room = f"research:{ticker}"
    await manager.connect(websocket, room)
    try:
        async for event in run_research_pipeline(ticker, company_name):
            await manager.broadcast(event, room)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        await manager.broadcast(
            {"type": "error", "data": {"message": str(exc)[:300]}}, room
        )
    finally:
        manager.disconnect(websocket, room)
