import pandas as pd

def compute_indicators(candles: list[dict]) -> dict:
    """candles: list of {open,high,low,close,volume} oldest first. Returns last indicators."""
    if len(candles) < 20:
        return {"rsi": None, "macd": None, "macd_signal": None, "bb_upper": None, "bb_lower": None, "ema50": None, "ema200": None, "sma20": None}

    df = pd.DataFrame(candles)
    close = df["close"]

    # RSI 14
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # EMA
    ema50 = close.ewm(span=50, adjust=False).mean()
    ema200 = close.ewm(span=200, adjust=False).mean()
    sma20 = close.rolling(20).mean()

    # MACD 12,26,9
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()

    # Bollinger 20,2
    std = close.rolling(20).std()
    bb_upper = sma20 + 2*std
    bb_lower = sma20 - 2*std

    last = -1
    return {
        "rsi": round(float(rsi.iloc[last]), 2) if pd.notna(rsi.iloc[last]) else None,
        "macd": round(float(macd.iloc[last]), 2) if pd.notna(macd.iloc[last]) else None,
        "macd_signal": round(float(macd_signal.iloc[last]), 2) if pd.notna(macd_signal.iloc[last]) else None,
        "bb_upper": round(float(bb_upper.iloc[last]), 2) if pd.notna(bb_upper.iloc[last]) else None,
        "bb_lower": round(float(bb_lower.iloc[last]), 2) if pd.notna(bb_lower.iloc[last]) else None,
        "ema50": round(float(ema50.iloc[last]), 2) if pd.notna(ema50.iloc[last]) else None,
        "ema200": round(float(ema200.iloc[last]), 2) if pd.notna(ema200.iloc[last]) else None,
        "sma20": round(float(sma20.iloc[last]), 2) if pd.notna(sma20.iloc[last]) else None,
        "close": float(close.iloc[last]),
        "volume": float(df["volume"].iloc[last]),
    }
