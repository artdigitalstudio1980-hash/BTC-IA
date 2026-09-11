.PHONY: up down test tf-validate
up:
	cp -n .env.example .env || true
	docker compose up --build

down:
	docker compose down

test:
	cd backend && python -m pytest -q
	cd frontend && npm test || npx jest --passWithNoTests

tf-validate:
	terraform -chdir=terraform fmt -check -recursive -diff
	terraform -chdir=terraform init -backend=false
	terraform -chdir=terraform validate
