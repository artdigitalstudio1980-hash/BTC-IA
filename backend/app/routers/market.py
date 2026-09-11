from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
import httpx
from ..db import get_db
from ..models import Candle
from ..config import settings
from ..indicators import compute_indicators

router = APIRouter(prefix="/api/market", tags=["market"])

@router.get("/candles")
def get_candles(symbol: str = Query("BTCUSDT"), interval: str = Query("1m"), limit: int = 100, db: Session = Depends(get_db)):
    q = db.query(Candle).filter(Candle.symbol==symbol.upper(), Candle.interval==interval).order_by(desc(Candle.open_time)).limit(limit).all()
    q = list(reversed(q))
    return [{"open_time": c.open_time.isoformat(), "open": c.open, "high": c.high, "low": c.low, "close": c.close, "volume": c.volume} for c in q]

@router.get("/indicators")
def get_indicators(symbol: str = Query("BTCUSDT"), interval: str = Query("1m"), db: Session = Depends(get_db)):
    candles = db.query(Candle).filter(Candle.symbol==symbol.upper(), Candle.interval==interval).order_by(Candle.open_time).all()
    arr = [{"open": c.open, "high": c.high, "low": c.low, "close": c.close, "volume": c.volume} for c in candles]
    ind = compute_indicators(arr)
    # enrich with latest price if empty
    if not arr:
        return {"symbol": symbol.upper(), "interval": interval, "indicators": ind, "count": 0}
    return {"symbol": symbol.upper(), "interval": interval, "indicators": ind, "count": len(arr)}

@router.get("/fear-greed")
async def fear_greed():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(settings.fear_greed_url)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"error": str(e), "data": [{"value": "50", "value_classification": "Neutral"}]}

@router.get("/btc")
def btc_legacy(db: Session = Depends(get_db)):
    # Backward compat for frontend mock
    candles = db.query(Candle).filter(Candle.symbol=="BTCUSDT").order_by(desc(Candle.open_time)).limit(1).first()
    if candles:
        return {"symbol": "BTCUSDT", "price": candles.close, "rsi": None, "note": "live"}
    return {"symbol": "BTCUSDT", "price": 63200, "rsi": 28, "note": "mock — waiting ingest"}
