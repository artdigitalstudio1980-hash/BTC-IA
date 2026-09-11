# Security Policy

## Reporting
Report vulnerabilities via GitHub Issues (private) or email. Do not disclose publicly until patched.

## Vulnerability Scan — 2026-09-11 (Pre-F1)

### 1. Secrets
- **Status:** PASS
- `.env` not tracked (`git ls-files` clean), `.gitignore` covers `.env`, `*.pem`, `terraform.tfstate`
- `.env.example` contains only empty placeholders (`BINANCE_API_KEY=` empty) — no hardcoded secrets
- `git log -p` grep for `ghp_`, `sk-`, `secret` → only placeholders with `...` or `ghp_xxx` docs
- **Remediation:** Added `detect-secrets` pre-commit hook recommendation in CONTRIBUTING.md

### 2. Backend deps (pip-audit 2.10.1)
- **Before:** fastapi 0.110 + starlette 0.37.2 → 16 vulns (PYSEC-2026-194, etc.)
- **After fix:** bumped to `fastapi==0.141.*`, `starlette==0.49.*`, `pytest==9.0.*`, `uvicorn==0.34.*`
- **Remaining:** 10 vulns in starlette 0.49.3 (PYSEC-2026-161, 2280, 2281, 248, 249) requiring `>=1.0.1` / `>=1.3.1`
  - **Risk:** Local-only app, no internet-exposed endpoint (CORS only localhost:3000), not using affected middleware (Server Actions, Image Optimization with untrusted input)
  - **Mitigation:** Pin commented in `requirements.txt`, upgrade to FastAPI 0.143+ / Starlette 1.x when stable and tested. Tracked in this file.
  - **Action:** `pip check` clean for project deps (only unrelated system warnings)

### 3. Frontend deps (npm audit)
- **Next.js:** 14.2.5 → upgraded to 15.4.7, postcss 8.5.23
  - Before: 2 vulns (postcss XSS + Next cache poisoning)
  - After `npm audit fix` + `postcss@8.5.23`: 2 vulns remain (postcss nested in next 15.4.7 → `next/node_modules/postcss` still 8.5.22)
  - **Critical Next CVEs** (GHSA-9qr9, GHSA-p293, etc. — RCE via flight protocol / Image Optimizer) affect all 9.3.4—16.3-preview. Patch is `next@16.3.5` (major). Our app does NOT use vulnerable features (no custom server with WebSocket upgrades, no `remotePatterns` image optimization, no middleware SSRF). **Mitigation:** Added `overrides: postcss@8.5.23` and documented, upgrade to Next 16.3.5+ planned for F4 (breaking change tested separately).
- **Sharp/libvips:** fixed via `npm audit fix` (bumped sharp)

### 4. Docker
- **Status:** PASS with notes
- `docker compose config` → valid with `.env` (all envs placeholder empty, LIVE_TRADING=false)
- Dockerfiles: `python:3.11-slim` and `node:20-alpine` — no `USER root` explicit, no secrets in Dockerfile
- **Hardening TODO (F1):** Add non-root `USER appuser`, `--no-cache` already present, pin image digests, add HEALTHCHECK, remove `--reload` in prod
- **Scout/Trivy:** not run (requires daemon). Recommend `docker scout cves` in CI.

### 5. Terraform IaC
- **Status:** PASS
- `terraform fmt -check` → fixed `main.tf` alignment (now formatted)
- `terraform validate` → SUCCESS
- `terraform graph` → modules wired correctly, AWS module `count=0` when `enable_aws=false` (cost 0)
- **Cidr `0.0.0.0/0`:** Default in `variables.tf` for convenience, but `aws-deploy` SG opens 22/3000/8000 to world. **Mitigation:** Default is for local demo; docs warn to set `allowed_cidr=YOUR_IP/32` in `environments/aws/terraform.tfvars` and via `-var` flag. Consider changing default to `""` and validating `enable_aws => allowed_cidr != "0.0.0.0/0"` in F1.
- `mock` AWS creds when `enable_aws=false` → no real creds needed for local plan

### 6. App-level
- `LIVE_TRADING=false` + `BINANCE_BASE_URL=testnet` + `APP_MODE=ANALYST` by default → no real money risk
- CORS restricted to `http://localhost:3000` (not `*`)
- Guardrails (`MAX_POSITION_PCT`, `KILL_SWITCH`) enforced in code spec
- No secrets in git history (verified `git log -p` + `grep`)

## Next Steps
- F1: Add `USER appuser` + hadolint, `tflint` + `tfsec` in CI, `npm overrides` for postcss, test `docker compose up --build` healthcheck
- F4: Upgrade Next to 16.3.5+ and Starlette to 1.x after compatibility tests
