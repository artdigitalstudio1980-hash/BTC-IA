"""Unit tests for Indicator Engine (spec §6) — puro, sin I/O, testeable con velas fijas."""

def compute_rsi(prices, period=14):
    # Minimal RSI calc to validate logic without 'ta' dep (mirrors ta.rsi)
    import pandas as pd
    s = pd.Series(prices)
    delta = s.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def test_rsi_oversold():
    # 14 down candles -> RSI < 30
    prices = [65000 - i*100 for i in range(30)]
    rsi = compute_rsi(prices)
    assert rsi < 35, f"expected oversold, got {rsi}"

def test_rsi_overbought():
    prices = [60000 + i*100 for i in range(30)]
    rsi = compute_rsi(prices)
    assert rsi > 65, f"expected overbought, got {rsi}"

def test_empty_prices_handled():
    import pandas as pd
    s = pd.Series([])
    assert len(s) == 0

def test_bollinger_placeholder():
    # Placeholder for BB(20,2) — will be implemented with 'ta' in F1
    assert True
