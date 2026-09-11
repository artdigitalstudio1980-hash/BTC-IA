from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager
from .config import settings
from .db import init_db, SessionLocal
from .routers import market, chat
from .ingestor import seed_history, ws_loop
import structlog

log = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # seed history (non-blocking)
    try:
        db = SessionLocal()
        await seed_history(db)
        db.close()
    except Exception as e:
        log.error("seed failed at startup", error=str(e))
    # start WS ingest in background if not in test
    task = None
    import os
    if not os.getenv("PYTEST_CURRENT_TEST"):
        task = asyncio.create_task(ws_loop(SessionLocal))
        log.info("ws_loop started")
    yield
    if task:
        task.cancel()

app = FastAPI(title="BTC-AI Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(chat.router)

@app.get("/health")
def health():
    return {"status": "ok", "mode": settings.app_mode, "live_trading": settings.live_trading, "ollama": settings.ollama_host, "symbols": settings.symbols}

@app.get("/api/market/btc")
def btc_mock():
    return {"symbol": "BTCUSDT", "price": 63200, "rsi": 28, "note": "deprecated — use /api/market/indicators?symbol=BTCUSDT"}
