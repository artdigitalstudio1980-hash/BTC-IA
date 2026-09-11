import asyncio
import json
import httpx
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from .models import Candle
from .config import settings, symbols_list
import structlog

log = structlog.get_logger()

BINANCE_WS = "wss://stream.binance.com:9443/ws"
BINANCE_REST = "https://api.binance.com"

async def fetch_klines_rest(symbol: str, interval: str, limit: int = 100):
    url = f"{BINANCE_REST}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()  # [openTime, open, high, low, close, volume, closeTime, ...]

def klines_to_candles(raw, symbol, interval):
    out = []
    for k in raw:
        out.append({
            "symbol": symbol,
            "interval": interval,
            "open_time": datetime.fromtimestamp(k[0]/1000, tz=timezone.utc),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
            "close_time": datetime.fromtimestamp(k[6]/1000, tz=timezone.utc),
        })
    return out

def save_candles(db: Session, candles: list[dict]):
    for c in candles:
        exists = db.query(Candle).filter_by(symbol=c["symbol"], interval=c["interval"], open_time=c["open_time"]).first()
        if not exists:
            db.add(Candle(**c))
    db.commit()

async def seed_history(db: Session):
    for sym in symbols_list():
        try:
            raw = await fetch_klines_rest(sym, settings.interval, limit=100)
            candles = klines_to_candles(raw, sym, settings.interval)
            save_candles(db, candles)
            log.info("seeded", symbol=sym, count=len(candles))
        except Exception as e:
            log.error("seed failed", symbol=sym, error=str(e))

# WebSocket ingest (reconnect with backoff) — runs as background task
async def ws_loop(db_factory, interval: str = None):
    interval = interval or settings.interval
    symbols = [s.lower() for s in symbols_list()]
    streams = "/".join([f"{s}@kline_{interval}" for s in symbols])
    url = f"{BINANCE_WS}/{streams}"
    backoff = 5
    import websockets
    while True:
        try:
            log.info("ws connecting", url=url)
            async with websockets.connect(url, ping_interval=20) as ws:
                backoff = 5
                async for msg in ws:
                    data = json.loads(msg)
                    k = data.get("k", {})
                    if not k:
                        continue
                    # only save closed candles to avoid spam, but also update last
                    symbol = k["s"]
                    candle = {
                        "symbol": symbol,
                        "interval": k["i"],
                        "open_time": datetime.fromtimestamp(k["t"]/1000, tz=timezone.utc),
                        "open": float(k["o"]),
                        "high": float(k["h"]),
                        "low": float(k["l"]),
                        "close": float(k["c"]),
                        "volume": float(k["v"]),
                        "close_time": datetime.fromtimestamp(k["T"]/1000, tz=timezone.utc),
                    }
                    db = db_factory()
                    try:
                        save_candles(db, [candle])
                    finally:
                        db.close()
                    if k.get("x"):  # closed
                        log.info("candle closed", symbol=symbol, close=candle["close"])
        except Exception as e:
            log.error("ws error", error=str(e), backoff=backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff*2, 60)
