# BTC-AI — Copiloto Cripto Local-First

> **Datos en tiempo real + IA local (Ollama) + 3 modos conmutables — tus claves nunca salen de tu PC.**

`ANALYST → ASSISTANT → AUTONOMOUS` · `Paper por defecto` · `1 comando` · `Open source`

---

## Instalación 1-comando

```bash
git clone https://github.com/<tu-usuario>/BTC-AI.git
cd BTC-AI
cp .env.example .env
docker compose up --build
docker exec btc-ai-ollama-1 ollama pull qwen2.5:7b-instruct
# Frontend http://localhost:3000  Backend http://localhost:8000
```

Pregunta en el chat: *"¿BTC está sobrevendido? Propón estrategia scalping 15m y haz backtest 30d"*

## Por qué

- **Privado:** Ollama local, nada va a la nube.
- **Seguro:** Arranca en `ANALYST` + `LIVE_TRADING=false` + Testnet. Sin dinero real hasta que tú lo actives.
- **Clonable:** Cualquiera con Docker lo levanta.
- **Explicable:** Toda estrategia viene con RSI, MACD, BB, EMA y Fear&Greed como contexto.

## Stack

`Python 3.11 + FastAPI + Next.js 14 + Postgres + Ollama + ccxt + Docker Compose` · Terraform opcional.

Ver [Spec de Diseño](./docs/superpowers/specs/2026-09-11-btc-ai-design.md).

## Terraform (Opcional)

No requerido para uso local. Ver [`terraform/README.md`](./terraform/README.md).

```bash
cd terraform && terraform init && terraform validate
terraform plan -var-file=environments/local/terraform.tfvars
# Deploy AWS opcional:
terraform apply -var-file=environments/aws/terraform.tfvars -var="enable_aws=true"
```

## Disclaimer

No es asesoramiento financiero. Ver [DISCLAIMER.md](./DISCLAIMER.md).
