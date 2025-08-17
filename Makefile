.PHONY: dev db-up db-down fmt

dev:
	bash scripts/dev.sh

db-up:
	docker compose -f docker-compose.dev.yml up -d db

db-down:
	docker compose -f docker-compose.dev.yml down -v

fmt:
	python -m black backend || true
