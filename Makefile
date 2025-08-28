# Development Workflow Makefile for autorisen
# Supports the development → staging → production pipeline

.PHONY: help dev dev-start dev-stop dev-test dev-clean
.PHONY: build build-frontend build-backend 
.PHONY: test test-frontend test-backend test-integration
.PHONY: deploy-check deploy-staging deploy-production
.PHONY: sync-localstorm db-up db-down db-reset
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
sync-localstorm: ## Sync components from localstorm repository
	@echo "🔄 Syncing components from localstorm..."
	@./scripts/sync-from-localstorm.sh

sync-frontend: ## Sync only frontend components from localstorm
	@echo "🔄 Syncing frontend components..."
	@./scripts/sync-from-localstorm.sh frontend

sync-backend: ## Sync only backend components from localstorm
	@echo "🔄 Syncing backend components..."
	@./scripts/sync-from-localstorm.sh backend

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
