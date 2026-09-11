# Contributing

1. `cp .env.example .env` y nunca commitees `.env`
2. `docker compose up --build`
3. `docker exec ollama ollama pull qwen2.5:7b-instruct`
4. Antes de PR: `docker compose config` + `cd terraform && terraform validate` + `pytest backend/tests` (cuando exista)
5. Commits en inglés, PRs contra `main`
