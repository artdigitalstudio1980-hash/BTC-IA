# BTC-AI — Local-First Crypto Copilot

> **Real-time market data + local AI (Ollama) + 3 switchable modes — your keys never leave your machine.**

`ANALYST (read-only) → ASSISTANT (propose + you approve) → AUTONOMOUS (24/7 with guardrails)` · `Paper by default` · `1-command setup` · `Open source`

[English] | [Español](./README_ES.md)

---

## Demo

```
git clone https://github.com/<you>/BTC-AI.git
cd BTC-AI
cp .env.example .env
docker compose up --build
# Frontend http://localhost:3000  Backend http://localhost:8000  Ollama http://localhost:11434
docker exec btc-ai-ollama-1 ollama pull qwen2.5:7b-instruct
```

Ask in chat: *"Is BTC oversold? Propose a 15m scalping strategy and backtest 30d"*

---

## Why BTC-AI?

- **Private:** Ollama runs locally, no cloud AI sees your trades.
- **Safe:** Starts in `ANALYST` + `LIVE_TRADING=false` + Binance Testnet. No real money moves until you explicitly enable it.
- **Clonable:** `docker compose up` is all you need. Terraform is optional.
- **Explainable:** Every strategy comes with indicators (RSI, MACD, BB, EMA, Fear & Greed) injected as context.

## Stack

`Python 3.11 + FastAPI + Next.js 14 + TypeScript + Tailwind + Postgres + Ollama (qwen2.5:7b) + ccxt + Docker Compose` · Terraform optional (`terraform/`).

See [Design Spec](./docs/superpowers/specs/2026-09-11-btc-ai-design.md) for architecture.

## 3 Modes

| Mode | What it does | Binance writes? |
|------|--------------|-----------------|
| `ANALYST` | Dashboard + Chat with real-time indicators, backtest | No |
| `ASSISTANT` | Proposes `Strategy{entry, sl, tp}` JSON → you click *Approve* → creates OCO | Only on approve (Testnet by default) |
| `AUTONOMOUS` | Rule-engine executes if `confidence>0.75` + `guardrails OK` | Yes, 24/7 |

Guardrails (enforced in code): `MAX_POSITION_PCT=5`, `MAX_DAILY_LOSS_PCT=2`, `KILL_SWITCH_FILE=/tmp/btc-ai-kill`, `LIVE_TRADING=false` by default.

## Quick Start (Local, no Terraform)

```bash
cp .env.example .env
docker compose up --build -d
docker exec $(docker ps -qf name=ollama) ollama pull qwen2.5:7b-instruct
open http://localhost:3000
# Try: POST http://localhost:8000/health
```

To enable trading (Testnet Paper):

```bash
# 1. Get Testnet keys: https://testnet.binance.vision/
# 2. Edit .env:
APP_MODE=ASSISTANT
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
BINANCE_BASE_URL=https://testnet.binance.vision
docker compose restart backend
```

Live trading: change `BINANCE_BASE_URL=https://api.binance.com` + `LIVE_TRADING=true` + restart. **Banner rojo** appears when live.

## Terraform (Optional IaC)

> Not required for `docker compose up`. Use when you want infra-as-code.

```bash
cd terraform
terraform init
terraform validate
# Local prereq check (no AWS needed):
terraform plan -var-file=environments/local/terraform.tfvars
# AWS deploy (creates EC2 + SG):
terraform apply -var-file=environments/aws/terraform.tfvars -var="enable_aws=true"
```

See [`terraform/README.md`](./terraform/README.md).

## Project Structure

```
BTC-AI/
├── docker-compose.yml
├── backend/ (FastAPI app/* + tests)
├── frontend/ (Next.js app/*)
├── ollama/Modelfile
├── terraform/{modules, environments}
└── docs/superpowers/specs/
```

## Roadmap

- **F0 Setup** → docker stack empty ✓
- **F1 Analyst** → BTC 1m ingest + indicators + dashboard + chat
- **F2 Assistant Paper** → strategy JSON + backtest + PaperExecutor
- **F3 Autonomous + TF** → scheduler + kill-switch + terraform/aws validated

## Disclaimer

Not financial advice. Paper by default. Use at your own risk. See [DISCLAIMER.md](./DISCLAIMER.md).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). PRs welcome. Run `terraform validate` + `docker compose config` before pushing.

## License

MIT — see [LICENSE](./LICENSE)
