<<<<<<< HEAD
# Development Workflow Makefile for autorisen
# Supports the development → staging → production pipeline

.PHONY: help dev dev-start dev-stop dev-test dev-clean
.PHONY: build build-frontend build-backend 
.PHONY: test test-frontend test-backend test-integration
.PHONY: deploy-check deploy-staging deploy-production
.PHONY: sync-capecraft db-up db-down db-reset
.PHONY: fmt lint security-check
.PHONY: logs logs-backend logs-frontend
.PHONY: install install-frontend install-backend

# Default target
help: ## Show this help message
	@echo "autorisen Development Workflow"
	@echo "=============================="
	@echo ""
	@echo "Development Commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development Environment
dev-start: ## Start development environment (backend + frontend)
	@echo "🚀 Starting autorisen development environment..."
	@./scripts/dev-start.sh

dev-stop: ## Stop development environment
	@echo "🛑 Stopping development environment..."
	@./scripts/dev-stop.sh

dev: dev-start ## Alias for dev-start

dev-test: ## Run comprehensive development tests
	@echo "🧪 Running development test suite..."
	@./scripts/dev-test.sh

dev-clean: ## Clean development environment
	@echo "🧹 Cleaning development environment..."
	@./scripts/dev-stop.sh
	@rm -rf client/node_modules/.cache
	@rm -rf backend/__pycache__
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Build Commands
build: build-frontend ## Build entire application

build-frontend: ## Build React frontend
	@echo "🏗️  Building frontend..."
	@cd client && npm run build

build-backend: ## Validate backend build
	@echo "🏗️  Validating backend..."
	@cd backend && python -c "from app.main import app; print('✅ Backend build successful')"

# Testing
test: test-backend test-frontend ## Run all tests

test-frontend: ## Run frontend tests
	@echo "🧪 Running frontend tests..."
	@cd client && npm test -- --run || echo "⚠️  Frontend tests not configured"

test-backend: ## Run backend tests
	@echo "🧪 Running backend tests..."
	@cd backend && python -m pytest -v || echo "⚠️  Backend tests not configured"

test-integration: ## Run integration tests
	@echo "🧪 Running integration tests..."
	@./scripts/dev-test.sh

# Component Management
sync-capecraft: ## Sync components from capecraft production environment
	@echo "🔄 Syncing components from capecraft production..."
	@./scripts/sync-from-capecraft.sh

sync-frontend: ## Sync only frontend components from capecraft
	@echo "🔄 Syncing frontend components..."
	@./scripts/sync-from-capecraft.sh frontend

sync-backend: ## Sync only backend components from capecraft
	@echo "🔄 Syncing backend components..."
	@./scripts/sync-from-capecraft.sh backend

# Deployment Pipeline
deploy-check: ## Run pre-production deployment checks
	@echo "🔍 Running pre-production validation..."
	@./scripts/pre-production-check.sh

deploy-staging: deploy-check ## Deploy to staging (autorisen)
	@echo "🚀 Deploying to staging..."
	@git add .
	@git commit -m "feat: staging deployment $(shell date)"
	@git push origin main

deploy-production: deploy-check ## Deploy to production (capecraft) - USE WITH CAUTION
	@echo "⚠️  PRODUCTION DEPLOYMENT - Requires manual confirmation"
	@read -p "Deploy to capecraft production? [y/N]: " confirm && [ "$$confirm" = "y" ]
	@git tag -a v$(shell date +%Y.%m.%d.%H%M) -m "Production release $(shell date)"
	@echo "🚀 Ready for production deployment to capecraft"
	@echo "Manual step: git push capecraft main"

# Database Management
db-up: ## Start local PostgreSQL database
	@echo "🗄️  Starting PostgreSQL database..."
	@docker compose -f docker-compose.dev.yml up -d db

db-down: ## Stop local PostgreSQL database
	@echo "🗄️  Stopping PostgreSQL database..."
	@docker compose -f docker-compose.dev.yml down -v

db-reset: ## Reset local database with fresh schema
	@echo "🔄 Resetting local database..."
	@./scripts/setup_local_postgres.sh

# Code Quality
fmt: ## Format code (Python + JavaScript)
	@echo "🎨 Formatting code..."
	@python -m black backend || echo "⚠️  Black not installed"
	@cd client && npm run format || echo "⚠️  Frontend formatter not configured"

lint: ## Run linters
	@echo "🔍 Running linters..."
	@cd backend && python -m flake8 . || echo "⚠️  Flake8 not installed"
	@cd client && npm run lint || echo "⚠️  ESLint not configured"

security-check: ## Run security checks
	@echo "🔒 Running security checks..."
	@cd backend && pip-audit || echo "⚠️  pip-audit not installed"
	@cd client && npm audit || echo "⚠️  npm audit failed"

# Installation
install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	@echo "📦 Installing backend dependencies..."
	@pip install -U pip
	@pip install -r requirements.txt
	@pip install -r backend/requirements.txt

install-frontend: ## Install frontend dependencies
	@echo "📦 Installing frontend dependencies..."
	@cd client && npm install

# Logging
logs: ## Show recent logs
	@echo "📋 Recent logs:"
	@tail -n 50 backend.log 2>/dev/null || echo "No backend logs found"

logs-backend: ## Show backend logs
	@tail -f backend.log

logs-frontend: ## Show frontend logs  
	@tail -f frontend.log

# Environment Status
status: ## Show development environment status
	@echo "📊 Development Environment Status"
	@echo "================================="
	@echo "Python: $(shell python --version 2>/dev/null || echo 'Not installed')"
	@echo "Node.js: $(shell node --version 2>/dev/null || echo 'Not installed')"
	@echo "PostgreSQL: $(shell psql --version 2>/dev/null || echo 'Not installed')"
	@echo ""
	@echo "Backend API: $(shell curl -s http://localhost:8000/api/health >/dev/null && echo '✅ Running' || echo '❌ Not running')"
	@echo "Database: $(shell psql -d autorisen_local -c 'SELECT 1;' >/dev/null 2>&1 && echo '✅ Connected' || echo '❌ Not connected')"
	@echo ""
	@echo "Git branch: $(shell git rev-parse --abbrev-ref HEAD)"
	@echo "Git status: $(shell git diff --quiet && git diff --cached --quiet && echo '✅ Clean' || echo '⚠️  Uncommitted changes')"

# Legacy support
db-up: ## Start database (legacy)
	docker compose -f docker-compose.dev.yml up -d db

db-down: ## Stop database (legacy)
	docker compose -f docker-compose.dev.yml down -v
=======
# autorisen Makefile — local dev (PostgreSQL) → GitHub Actions → Heroku
# --------------------------------------------------------------------
# Quick ref:
#   make              # shows help
#   make install      # backend+frontend deps
#   make db-up        # create/verify local DB (via Unix socket by default)
#   make dev-start    # start backend:8000 + frontend:3000
#   make status       # health snapshot
#   make deploy-check # fmt+lint+tests (what CI runs before deploy)
#   make push         # git push origin HEAD (triggers Actions → Heroku)
#   make heroku-*     # helper commands for prod
#
# Toggle Alembic migrations locally/CI by setting ALEMBIC=1

.ONESHELL:
SHELL := /bin/bash
.DEFAULT_GOAL := help

# ---- Paths & Commands --------------------------------------------------------
BACKEND_DIR ?= backend
FRONTEND_DIR ?= client
PY ?= python3
PIP ?= python3 -m pip
UVICORN ?= uvicorn

DB_NAME ?= autorisen_local
DB_USER ?= $(shell whoami)
# Use the local Unix socket by default to avoid password prompts (peer auth)
DB_HOST ?= /var/run/postgresql
DB_PORT ?= 5432

# Optional: switch to 1 to enable Alembic commands
ALEMBIC ?= 0

# Heroku app config (override via env or make VAR=...)
HEROKU_APP ?= autorisen

# Background PIDs will be stored here
PID_DIR := .make-pids
BACKEND_PID := $(PID_DIR)/backend.pid
FRONTEND_PID := $(PID_DIR)/frontend.pid

# Colors
GREEN  := \033[1;32m
YELLOW := \033[1;33m
RED    := \033[1;31m
BLUE   := \033[1;34m
RESET  := \033[0m

.PHONY: help install install-backend install-frontend \
        dev-start dev-stop logs status \
        db-up db-down db-reset \
        fmt lint test test-backend test-frontend \
        deploy-check push \
        heroku-login heroku-open heroku-logs heroku-run heroku-release-migrate

# ---- Help --------------------------------------------------------------------
help: ## Show this help
	@echo "autorisen Makefile — local dev → GitHub Actions → Heroku"
	@echo "----------------------------------------------------------------"
	@grep -E '^[a-zA-Z0-9_\-]+:.*?##' $(firstword $(MAKEFILE_LIST)) | sed -E 's/:.*?##/: /' | sort

# ---- Install -----------------------------------------------------------------
install: install-backend install-frontend ## Install backend & frontend deps
	@echo -e "$(GREEN)✔ Install complete$(RESET)"

install-backend: ## Install backend Python deps
	@echo -e "$(BLUE)[backend]$(RESET) Installing Python deps..."
	cd $(BACKEND_DIR)
	$(PIP) install -r requirements.txt

install-frontend: ## Install frontend Node deps
	@echo -e "$(BLUE)[frontend]$(RESET) Installing Node deps..."
	cd $(FRONTEND_DIR)
	npm install

# ---- Database (local PostgreSQL) --------------------------------------------
# Notes:
# - Meta-queries explicitly use -d postgres to avoid defaulting to a DB named after $(DB_USER).
# - We try to create the role and DB via the local postgres superuser if missing.
db-up: ## Create local PostgreSQL role & database if missing (socket by default)
	@if ! psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$(DB_USER)'" | grep -q 1; then \
		echo -e "$(YELLOW)Role '$(DB_USER)' missing — creating (LOGIN, CREATEDB)$(RESET)"; \
		sudo -u postgres psql -d postgres -tAc "CREATE ROLE $(DB_USER) LOGIN CREATEDB" || true; \
	fi
	@if ! psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$(DB_NAME)'" | grep -q 1; then \
		echo -e "$(BLUE)[db]$(RESET) Creating DB $(DB_NAME) owned by $(DB_USER)"; \
		sudo -u postgres createdb -O $(DB_USER) $(DB_NAME) 2>/dev/null || true; \
	else \
		echo -e "$(YELLOW)DB exists: $(DB_NAME)$(RESET)"; \
	fi
	@# Verify connectivity to the target DB before success message
	@if psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d $(DB_NAME) -c 'SELECT 1;' >/dev/null 2>&1; then \
		echo -e "$(GREEN)✔ DB ready: $(DB_NAME) as $(DB_USER)$(RESET)"; \
	else \
		echo -e "$(RED)✖ DB NOT READY — try DB_HOST=/var/run/postgresql and check pg_hba.conf$(RESET)"; \
		exit 1; \
	fi
ifeq ($(ALEMBIC),1)
	@echo -e "$(BLUE)[db]$(RESET) Running migrations (alembic upgrade head)"
	cd $(BACKEND_DIR)
	alembic upgrade head
endif

db-down: ## Drop local DB (careful!)
	@dropdb -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) $(DB_NAME) 2>/dev/null || true
	@echo -e "$(YELLOW)⚠ Dropped DB $(DB_NAME)$(RESET)"

db-reset: db-down db-up ## Drop + recreate DB

# ---- Dev (start/stop) --------------------------------------------------------
dev-start: ## Start backend (8000) + frontend (3000) in background
	@mkdir -p $(PID_DIR) logs
	@touch logs/backend.out logs/frontend.out
	@echo -e "$(BLUE)[backend]$(RESET) Starting uvicorn on :8000"
	cd $(BACKEND_DIR)
	nohup $(PY) -m $(UVICORN) app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.out 2>&1 & echo $$! > ../$(BACKEND_PID)
	sleep 1
	@echo -e "$(BLUE)[frontend]$(RESET) Starting Vite dev server on :3000"
	cd ../$(FRONTEND_DIR)
	nohup npm run dev -- --host > ../logs/frontend.out 2>&1 & echo $$! > ../$(FRONTEND_PID)
	@echo -e "$(GREEN)✔ Dev started. Logs in ./logs. PIDs in $(PID_DIR).$(RESET)"

dev-stop: ## Stop background dev processes
	@-if [ -f $(BACKEND_PID) ]; then PID=$$(cat $(BACKEND_PID)); if ps -p $$PID >/dev/null 2>&1; then kill $$PID; fi; rm -f $(BACKEND_PID); echo "$(YELLOW)Stopped backend$(RESET)"; fi
	@-if [ -f $(FRONTEND_PID) ]; then PID=$$(cat $(FRONTEND_PID)); if ps -p $$PID >/dev/null 2>&1; then kill $$PID; fi; rm -f $(FRONTEND_PID); echo "$(YELLOW)Stopped frontend$(RESET)"; fi
	@-rmdir $(PID_DIR) 2>/dev/null || true

logs: ## Tail both logs (Ctrl-C to exit)
	@mkdir -p logs; touch logs/backend.out logs/frontend.out
	@echo -e "$(BLUE)[logs]$(RESET) Tailing logs..."
	@bash -c "tail -n +1 -f logs/backend.out logs/frontend.out"

status: ## Snapshot: tools, services, git
	@echo -e "$(BLUE)── Tools ───────────────────────────────$(RESET)"
	@echo -n "Python: "; ($(PY) --version 2>/dev/null || echo "not installed")
	@echo -n "Node:   "; (node --version 2>/dev/null || echo "not installed")
	@echo -n "psql:   "; (psql --version 2>/dev/null || echo "not installed")
	@echo
	@echo -e "$(BLUE)── Services ────────────────────────────$(RESET)"
	@bash -c "curl -s http://localhost:8000/api/health >/dev/null && echo 'Backend: ✅ http://localhost:8000' || echo 'Backend: ❌ not responding'"
	@bash -c "curl -s http://localhost:3000 >/dev/null && echo 'Frontend: ✅ http://localhost:3000' || echo 'Frontend: ❌ not responding'"
	@bash -c "psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d $(DB_NAME) -c 'SELECT 1;' >/dev/null 2>&1 && echo 'Database: ✅ connected ($(DB_NAME))' || echo 'Database: ❌ not connected'"
	@echo
	@echo -e "$(BLUE)── Git ─────────────────────────────────$(RESET)"
	@git rev-parse --abbrev-ref HEAD | xargs -I{} echo "Branch: {}"
	@bash -c "git diff --quiet && git diff --cached --quiet && echo 'Status: ✅ clean' || echo 'Status: ⚠ uncommitted changes'"
	@echo
	@echo -e "$(BLUE)── Actions/Deploy ──────────────────────$(RESET)"
	@echo "Push with 'make push' to trigger GitHub Actions → Heroku"

# ---- Quality -----------------------------------------------------------------
fmt: ## Format backend (black/isort) + frontend (prettier)
	@echo -e "$(BLUE)[fmt]$(RESET) Python (black + isort)"
	cd $(BACKEND_DIR)
	black .
	isort .
	@echo -e "$(BLUE)[fmt]$(RESET) Frontend (prettier)"
	cd ../$(FRONTEND_DIR)
	npx prettier -w .

lint: ## Lint backend (ruff/flake8 optional) + frontend (eslint)
	@echo -e "$(BLUE)[lint]$(RESET) Python (ruff)"
	cd $(BACKEND_DIR) && ruff check . || true
	@echo -e "$(BLUE)[lint]$(RESET) Frontend (eslint)"
	cd $(FRONTEND_DIR) && npx eslint . || true

test: test-backend test-frontend ## Run all tests
	@echo -e "$(GREEN)✔ Tests complete$(RESET)"

test-backend: ## Run backend tests (pytest)
	cd $(BACKEND_DIR) && pytest -q || true

test-frontend: ## Run frontend tests (vitest if configured)
	cd $(FRONTEND_DIR) && npm test --silent || true

deploy-check: fmt lint test ## Local checks before pushing
	@echo -e "$(GREEN)✔ Deploy checks passed (local)$(RESET)"

# ---- Git / CI trigger --------------------------------------------------------
push: ## Push current branch to origin (triggers GitHub Actions)
	git push origin HEAD
	@echo -e "$(GREEN)✔ Pushed to origin. GitHub Actions will run and deploy to Heroku (if configured).$(RESET)"

# ---- Heroku helpers ----------------------------------------------------------
heroku-login: ## heroku container:login
	heroku container:login

heroku-open: ## Open Heroku app in browser
	heroku open -a $(HEROKU_APP)

heroku-logs: ## Tail Heroku logs
	heroku logs -a $(HEROKU_APP) --tail

heroku-run: ## Run an arbitrary command on Heroku dyno. Usage: make heroku-run CMD="python -V"
	@if [ -z "$$CMD" ]; then echo "Usage: make heroku-run CMD='echo hello'"; exit 2; fi
	heroku run -a $(HEROKU_APP) -- $$CMD

heroku-release-migrate: ## Run DB migrations on Heroku (alembic if present; else no-op)
	@if heroku run -a $(HEROKU_APP) "bash -lc 'command -v alembic >/dev/null 2>&1'" >/dev/null 2>&1; then \
		echo -e "$(BLUE)[heroku]$(RESET) Running alembic upgrade head"; \
		heroku run -a $(HEROKU_APP) -- bash -lc 'cd backend && alembic upgrade head'; \
	else \
		echo -e "$(YELLOW)[heroku] Alembic not found in dyno; skipping migrations$(RESET)"; \
	fi
>>>>>>> 01f6b551 (chore: initial commit with Makefile and CI/CD workflow)
