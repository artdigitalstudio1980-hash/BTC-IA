from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_mode: str = "ANALYST"  # ANALYST | ASSISTANT | AUTONOMOUS
    live_trading: bool = False
    database_url: str = "postgresql://btcai:btcai@postgres:5432/btcai"
    ollama_host: str = "http://ollama:11434"
    ollama_model: str = "qwen2.5:7b-instruct"
    ollama_fallback: str = "llama3.1:8b"
    symbols: str = "BTCUSDT,ETHUSDT,SOLUSDT"
    interval: str = "1m"
    fear_greed_url: str = "https://api.alternative.me/fng/?limit=1"
    binance_api_key: str = ""
    binance_api_secret: str = ""
    binance_base_url: str = "https://testnet.binance.vision"
    max_position_pct: float = 5.0
    max_daily_loss_pct: float = 2.0
    kill_switch_file: str = "/tmp/btc-ai-kill"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

def symbols_list():
    return [s.strip().upper() for s in settings.symbols.split(",") if s.strip()]
