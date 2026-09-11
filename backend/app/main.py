from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BTC-AI Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "mode": "ANALYST", "ollama": "http://ollama:11434"}

@app.get("/api/market/btc")
def btc_mock():
    return {"symbol": "BTCUSDT", "price": 63200, "rsi": 28, "note": "MVP mock — ingestor viene en F1"}
