import httpx
from .config import settings

SYSTEM_PROMPT = """Eres BTC-AI, copiloto cripto local. Respondes en español si el usuario escribe en español.
Siempre que propongas estrategia, incluye bloque ```json con {symbol, entry, stop_loss, take_profit, timeframe, rationale, confidence 0-1}.
Nunca inventes precios: usa solo el contexto que te inyecta el backend (OHLCV, RSI, MACD, BB, Fear&Greed).
Advierte riesgo y recomienda Paper/Testnet antes de Live. Eres conciso y accionable."""

async def chat_stream(messages, context: dict):
    """Proxy streaming to Ollama /api/chat. Yields SSE chunks. Falls back to mock if Ollama down."""
    payload = {
        "model": settings.ollama_model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT + f"\n\nContexto mercado:\n{context}"}] + messages,
        "stream": True,
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream("POST", f"{settings.ollama_host}/api/chat", json=payload) as r:
                if r.status_code != 200:
                    yield f"data: Ollama no disponible ({r.status_code}). Corre: ollama pull {settings.ollama_model}\n\n"
                    return
                async for line in r.aiter_lines():
                    if line:
                        # Ollama returns JSON lines {"message":{"content":"..."}}
                        try:
                            import json
                            j = json.loads(line)
                            content = j.get("message", {}).get("content") or j.get("response", "")
                            if content:
                                yield f"data: {content}\n\n"
                            if j.get("done"):
                                break
                        except Exception:
                            yield f"data: {line}\n\n"
                yield "data: [DONE]\n\n"
    except Exception as e:
        # Fallback mock so UI still useful without Ollama
        yield f"data: (Mock — Ollama no disponible: {e})\n\n"
        yield f"data: Contexto recibido: {context}\n\n"
        yield f"data: Con RSI={context.get('rsi')} y precio {context.get('price')}, estrategia sugerida: scalping 15m con entrada ~{context.get('price')} y SL -1.5% / TP +2% (Paper).\n\n"
        yield "data: [DONE]\n\n"
