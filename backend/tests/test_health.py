from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "ok"
    assert j["mode"] == "ANALYST"
    assert "ollama" in j

def test_cors_headers():
    r = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert r.status_code == 200
    # CORSMiddleware should allow localhost:3000
    assert r.headers.get("access-control-allow-origin") in ("http://localhost:3000", "*")

def test_btc_mock():
    r = client.get("/api/market/btc")
    assert r.status_code == 200
    j = r.json()
    assert j["symbol"] == "BTCUSDT"
    assert isinstance(j["price"], (int, float))
    assert "rsi" in j

def test_btc_mock_not_trading_without_env():
    # LIVE_TRADING false by default — no real trade endpoint yet
    r = client.get("/api/market/btc")
    assert r.status_code != 500
