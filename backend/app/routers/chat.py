from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..db import get_db
from ..models import Candle
from ..indicators import compute_indicators
from ..ollama import chat_stream
from ..config import settings
import httpx

router = APIRouter(prefix="/api", tags=["chat"])

def build_context(db: Session):
    # BTCUSDT 1m last 100 -> indicators + fear&greed best effort
    candles = db.query(Candle).filter(Candle.symbol=="BTCUSDT", Candle.interval==settings.interval).order_by(Candle.open_time).all()
    arr = [{"open": c.open, "high": c.high, "low": c.low, "close": c.close, "volume": c.volume} for c in candles]
    ind = compute_indicators(arr)
    # fear greed sync fallback
    fg = "50 Neutral"
    try:
        import requests
        r = requests.get(settings.fear_greed_url, timeout=3)
        if r.ok:
            d = r.json()["data"][0]
            fg = f"{d['value']} {d['value_classification']}"
    except Exception:
        pass
    price = ind.get("close") or 63200
    return {
        "symbol": "BTCUSDT",
        "price": price,
        "interval": settings.interval,
        "rsi": ind.get("rsi"),
        "macd": ind.get("macd"),
        "bb_upper": ind.get("bb_upper"),
        "bb_lower": ind.get("bb_lower"),
        "ema50": ind.get("ema50"),
        "ema200": ind.get("ema200"),
        "fear_greed": fg,
        "candles_count": len(arr),
    }

@router.post("/chat/stream")
async def chat_stream_endpoint(body: dict, db: Session = Depends(get_db)):
    messages = body.get("messages", [])
    # body.messages: [{role, content}]
    context = build_context(db)
    return StreamingResponse(chat_stream(messages, context), media_type="text/event-stream")

@router.post("/chat")
async def chat(body: dict, db: Session = Depends(get_db)):
    messages = body.get("messages", [])
    context = build_context(db)
    # non-streaming: collect
    chunks = []
    async for c in chat_stream(messages, context):
        if c.startswith("data: ") and not c.strip().endswith("[DONE]"):
            chunks.append(c[6:].strip())
    return {"context": context, "reply": "".join(chunks)}
