# BTC-AI — Design Spec — 2026-09-11

## 1. Overview
**BTC-AI** es un copiloto cripto **local-first, 100% privado** que corre en la PC del usuario via `docker-compose up`. Ingesta datos de mercado en tiempo real (Binance WS), calcula indicadores técnicos, los analiza con IA local (Ollama), y permite conversar en un chat para generar estrategias. Opera en 3 modos conmutables: `ANALYST → ASSISTANT → AUTONOMOUS`. Repo público clonable pensado para que cualquiera lo descargue y configure con sus propias claves.

**Stack A elegido:** `Python 3.11 + FastAPI (async) + Next.js 14 + TypeScript + Tailwind + Postgres + Ollama (qwen2.5:7b) + ccxt + Docker Compose 1-comando`. Terraform opcional para IaC (ver §11).

## 2. Propósito y Principios
- **Problema:** Bots en la nube custodian claves, TradingView premium costoso, ChatGPT ve tus datos/trades.
- **Solución:** Todo local, claves nunca salen, coste IA = 0, open-source.
- **Principios:** `local-first > cloud-optional`, `paper-by-default > live-with-guardrails`, `modular > monolith spaghetti`, `clonable in <10min`, `no secrets in repo`.

## 3. Usuarios y Casos de Uso
- **Trader retail técnico:** quiere copiloto analista + semi-auto sin ceder claves.
- **Dev open-source:** quiere clonar, self-hostear, contribuir.
- **NO usuarios:** no-técnicos sin Docker (Fase 2 con instalador Tauri).

**Casos:**
- UC1: "¿BTC sobrevendido?" → chat responde con RSI, BB, Fear&Greed y propone estrategia scalping 15m + backtest 30d.
- UC2: Aprobar estrategia propuesta → crea OCO en Binance Testnet.
- UC3: Modo AUTONOMOUS deja bot 24h en Testnet con kill-switch.

## 4. No-Goals (V1)
- No Futures con apalancamiento en MVP (Fase 3).
- No multi-exchange en MVP (solo Binance).
- No mobile app nativa.
- No predicción de precio con ML entrenado (solo IA generativa sobre indicadores).

## 5. Arquitectura — Enfoque 1 Monolito Modular (Recomendado V1)

```
[Binance WS/REST] ──► [Ingestor Service (asyncio)] ──► [Indicator Engine] ──┐
[Alt.me Fear&Greed] ───────────────────────────────► [Market Store (Postgres)] │
                                                                               ├──► [Strategy Engine (JSON schema)] ──► [Executor (ccxt)] ──► [Binance API]
                                                                               │
[Usuario] ◄── WS/SSE ◄── [FastAPI :8000] ◄── [Ollama Agent (qwen2.5:7b)] ◄─────┘
   ▲                          │
   └──── [Next.js :3000] ─────┘
         [Ollama :11434]
```

**Servicios docker-compose.yml:**
- `backend` (FastAPI :8000), `frontend` (Next.js :3000), `ollama` (:11434), `postgres` (:5432) + `pgdata` volume. Redis opcional V2.

**Evolución:** Enfoque 2 Event-Driven (Redis Streams) y Enfoque 3 Tauri desktop documentados como ADR, sin implementar en V1. Boundaries limpios permiten migrar sin romper.

## 6. Componentes Aislados
| Módulo | Responsabilidad | Interface | Depende de |
|--------|-----------------|-----------|------------|
| `backend/app/ingestor` | Conecta WS `btcusdt@kline_1m`, normaliza OHLCV, reconexión exponential backoff | `subscribe(symbols, interval): AsyncGenerator[Candle]` | Binance WS |
| `backend/app/indicators` | Puro `ohlcv -> {rsi, macd, bb, ema}` via `ta` | `compute(candles) -> Indicators` | ninguno (testeable) |
| `backend/app/market_store` | CRUD velas, queries backtest | `save(candles)`, `get(symbol, since)` | Postgres |
| `backend/app/ollama_agent` | Prompt templating + RAG (inyecta últimos indicadores), tools `get_price, get_rsi, propose_strategy` | `POST /chat/stream` SSE | Ollama |
| `backend/app/strategy_engine` | Valida `Strategy{entry, stop_loss, take_profit, timeframe, confidence}` con pydantic JSON schema | `validate(json) -> Strategy` | market_store |
| `backend/app/executor` | Único con permiso de firmar Binance. `PaperExecutor` vs `LiveExecutor` | `execute(strategy) -> Order` | ccxt, guardrails |
| `backend/app/guardrails` | `max_daily_loss, max_position_pct=5%, kill-switch, LIVE_TRADING flag` | `check(order) -> bool` | config |
| `frontend` | Dashboard velas (Lightweight-Charts), panel indicadores, chat streaming markdown | `fetch /api/*` | backend |

## 7. Flujo Chat → Estrategia → Ejecución
1. Usuario: "propón scalping 15m"
2. Frontend → `POST /chat/stream` → backend inyecta contexto `BTC $63.2k RSI14=28 BB lower Fear=22 vol+35%`
3. Ollama stream markdown + bloque ```json strategy```
4. `ANALYST`: muestra + botón Backtest (simula 30d).
5. `ASSISTANT`: botón "Aprobar en Testnet" → `POST /strategies/approve` → OCO Testnet.
6. `AUTONOMOUS`: si `confidence>0.75` y `guardrails OK` → ejecuta y logea `/trades`.
- Errores: WS caído → fallback REST polling 1m + banner. Ollama caído → "corre `ollama pull qwen2.5:7b`". Binance 429 → circuit breaker 60s.

## 8. APIs e Integraciones
- **Binance:** WS `wss://stream.binance.com:9443/ws/btcusdt@kline_1m` + REST `api.binance.com` via `ccxt`. Testnet `testnet.binance.vision` para Paper.
- **Fear & Greed:** `GET https://api.alternative.me/fng/?limit=1`
- **CoinGecko (opcional B/C):** `GET /coins/markets` para top10.
- **Ollama:** `POST http://ollama:11434/api/chat` (OpenAI-compatible). Modelos: `qwen2.5:7b-instruct` default, `llama3.1:8b` fallback. ` Modelfile` custom con system prompt trader.

## 9. 3 Modos — Configuración
- `APP_MODE=ANALYST|ASSISTANT|AUTONOMOUS` (env + toggle UI)
- `LIVE_TRADING=false` por defecto. `true` requiere `BINANCE_API_KEY+SECRET` + confirmación manual + 2FA si se configura Telegram.
- Guardrails forzados en código: `MAX_POSITION_PCT=5`, `MAX_DAILY_LOSS_PCT=2`, `KILL_SWITCH_FILE=/tmp/btc-ai-kill`.

## 10. Métricas MVP (Core A)
- OHLCV 1m/15m/1h/1d, volumen, RSI14, MACD, BB(20,2), EMA50/200, Order Book top10 bid/ask, Fear&Greed. BTC/USDT default, configurable `SYMBOLS=BTCUSDT,ETHUSDT,SOLUSDT` via .env.

## 11. Terraform — IaC Opcional (Nuevo Requisito)
**Filosofía:** Local por defecto **NO requiere Terraform** (`docker-compose up` es suficiente). `terraform/` es capa opcional para reproducibilidad, CI y deploy cloud.

**Estructura:**
```
terraform/
├── README.md
├── versions.tf        # required_version >=1.5, providers: docker, github, aws
├── variables.tf       # project_name, env, symbols, enable_aws
├── outputs.tf         # repo_url, backend_url
├── main.tf            # root que llama módulos
├── modules/
│   ├── github-repo/   # github_repository, github_branch_protection, github_actions_secret
│   ├── docker-host/   # docker_image, docker_container check prereqs via null_resource
│   └── aws-deploy/    # VPC, EC2 t3.medium + docker, ECR, SG, IAM role (count=0 si enable_aws=false)
└── environments/
    ├── local/         # terraform.tfvars local (enable_aws=false)
    └── aws/           # terraform.tfvars aws (enable_aws=true, instance_type)
```

**Uso:**
- Local: `cd terraform && terraform init && terraform apply -var-file=environments/local/terraform.tfvars` → valida docker/ollama instalados, opcionalmente crea repo GitHub si `GITHUB_TOKEN` seteado. No levanta infra cloud.
- Cloud: `terraform apply -var-file=environments/aws/terraform.tfvars -var="enable_aws=true"` → crea EC2 con user_data que clona repo + docker-compose up + security group 3000/8000 restringido por `allowed_cidr`.
- `count`/`for_each` en módulos AWS para que por defecto coste = 0.
- State local `terraform.tfstate` gitignored; para equipo se documenta backend S3 opcional.

**Ventaja repo público:** Contribuidores ven infra como código, reproducen entorno idéntico, CI puede validar `terraform validate` + `tflint`.

## 12. Estructura Repo
```
BTC-AI/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md / README_ES.md
├── DISCLAIMER.md / LICENSE (MIT) / CONTRIBUTING.md
├── docs/superpowers/specs/2026-09-11-btc-ai-design.md
├── backend/{Dockerfile, requirements.txt, app/*, tests/}
├── frontend/{Dockerfile, package.json, app/*}
├── ollama/Modelfile
└── terraform/{...}
```

## 13. Fases y Criterios de Aceptación
- **F0 Setup (1-2d):** docker-compose base + terraform validate OK. Criterio: `docker-compose up` levanta stack vacío.
- **F1 MVP Analyst (1w):** Ingestor BTC 1m + Postgres + indicadores + dashboard + chat Ollama. Criterio: "analiza BTC ahora" responde con datos últimos 5m reales.
- **F2 Assistant Paper (1w):** Strategy JSON + backtest 30d + PaperExecutor Testnet + botón aprobar + guardrails. Criterio: orden simulada visible en Testnet.
- **F3 Autonomous + TF (1w):** Scheduler + kill-switch + max_loss + Telegram opcional + terraform/aws validado. Criterio: bot 24h Testnet sin intervención, PnL log.
- **F4 Hardening (3d):** tests pytest indicador, CI GH Actions (docker up + terraform validate + tflint), demo GIF, Release. Criterio: tercero clona en Windows limpio <10min siguiendo README.

## 14. Seguridad Repo Público
- `.env` nunca commiteado, `pre-commit` detect-secrets, `.env.example` con placeholders.
- `DISCLAIMER`: no asesoramiento financiero, Paper por defecto.
- Branch protection via terraform/github-repo.
- Binance keys solo en env local o GH Secrets para CI mock.

## 15. Testing & Observabilidad
- `pytest` indicadores con velas fijas (sin red). `httpx` mock Binance/Ollama.
- Frontend `vitest` + `playwright` smoke.
- Logs `structlog` JSON, `GET /health` (ingestor, ollama, db).
- `terraform validate` + `tflint` en CI.

## 16. Decisiones (ADR)
- ADR1: FastAPI vs NestJS → FastAPI por `ccxt/ta` Python.
- ADR2: Ollama 100% local vs híbrido → Local puro por requisito usuario.
- ADR3: Docker Compose vs K8s → Compose por clonabilidad.
- ADR4: Terraform opcional vs obligatorio → Opcional para no friccionar local.

## 17. Riesgos
- Ollama VRAM >8GB requerido → documentar `qwen2.5:3b` fallback.
- Binance WS ban → circuit breaker + backoff.
- Paper vs Live confusión → banner rojo persistente cuando `LIVE_TRADING=true`.

---
Aprobado por: usuario 2026-09-11. Próximo: `writing-plans` → plan implementación.
