# 🛠 DEVELOPMENT CONTEXT

**Last Updated**: September 2, 2025
**Source of truth**: CapeControl / Capecraft project (synchronized with latest Heroku deployment logs)  
**Project Status**: Production Ready — Registration fixed, AI Security Suite deployed, Payment & Developer Earnings live  
**Current Version**: v663 (Heroku, deployed Aug 17, 2025) ✅ RUNNING
**Latest Update**: Local PostgreSQL development environment configured with automated database duplication
**Database Status**: ✅ Local PostgreSQL setup complete with Heroku schema replication

---

## Executive Summary

This document captures the authoritative development and deployment context for the CapeControl / Capecraft project, incorporating `autorisen` features into the main CapeControl platform.

- **Production App**: `capecraft` (Heroku, version v663)
- **Staging Source**: `autorisen` repo, feature integration validated here
- **Goal**: Feature-flagged integration of `autorisen` modules into CapeControl, with validation gates before production promotion.

---

## 1. Company Information

- **Legal Entity**: Cape Craft Projects CC
- **Trading Name**: Cape Control
- **VAT Number**: 4270105119

---

## 2. Project Status & Versions

- **Production**: Heroku app `capecraft` (v663, deployed Aug 17, 2025, release `f8783ce4`)
- **Staging Source**: `autorisen` (used for integration testing)
-- **Backend**: FastAPI 0.110.0 on Python 3.12
- **Frontend**: React 18 + Vite, served by FastAPI
- **Stripe**: integration deployed and test-ready (Heroku-compatible at `stripe==7.7.0`)

---

## 3. Repositories & Structure

- **Production Repo**: `localstorm` / `capecontrol` (contains `backend/` and `client/`)
- **Staging Repo**: `autorisen` (features to be merged under `apps/autorisen` or `backend/app/routes/autorisen`)

---

## 4. Development Workflow

### Component Source Management
- **Source Repository**: If any components are missing from the autorisen project, they should be copied from **capecraft production environment** (Heroku)
- **Development Priority**: The autorisen project must always be ahead of capecraft in development lifecycle

### Deployment Pipeline Strategy
1. **Development Phase**: Build and test all functionality on autorisen first
2. **Testing Phase**: Ensure complete functionality validation before promotion  
3. **Production Deployment**: Push to capecraft (live site) only after thorough testing
4. **Service Continuity**: Maintain zero disruption to live services
5. **Uptime Requirements**: Ensure absolute minimal downtime during deployments

### Quality Assurance Protocol
- All features must be fully tested in autorisen environment
- No untested code should reach the capecraft production environment
- Maintain service reliability and user experience standards

This workflow ensures a proper **development → staging → production** pipeline where autorisen serves as the development/staging environment and capecraft is the protected production environment.

### Local Development Environment Setup

The project now supports both SQLite (default) and PostgreSQL development environments.

#### Option A: Quick SQLite Setup (Default)

1. Create & activate a repo venv (if not present):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install backend dependencies:

```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
# Optional: pip install -r backend/requirements-dev.txt
```

3. Create a `.env` from the example (defaults will use SQLite):

```bash
cp .env.example .env
# By default the app uses: DATABASE_URL=sqlite:///./capecontrol.db
```

#### Option B: PostgreSQL Development Environment (Recommended for Production Parity)

**Prerequisites**: PostgreSQL 16+ installed locally

1. **Automated Setup**: Use the provided script to create a local database with production schema:

```bash
# Run the automated setup script
bash ./scripts/setup_local_postgres.sh "postgres://[HEROKU_DATABASE_URL]" autorisen_local vscode

# This script will:
# - Create local PostgreSQL database 'autorisen_local' 
# - Dump production schema from Heroku
# - Restore schema to local database
# - Update .env with local DATABASE_URL
# - Set up 'vscode' user with proper permissions
```

2. **Manual Database Connection**:

```bash
# Connect to your local database
PGPASSWORD=123456 psql -h localhost -U vscode -d autorisen_local

# View tables
\dt

# Exit
\q
```

3. **Database Schema**: The local database contains production-identical tables:
   - `users_v2` - User accounts and authentication
   - `tokens_v2` - Authentication tokens and sessions
   - `developer_earnings_v2` - Developer payment tracking
   - `password_resets_v2` - Password reset functionality  
   - `audit_logs_v2` - Security audit trail

#### Starting the Application

4. Start the backend using the repo helper (activates venv, sets PYTHONPATH, writes logs to /tmp):

```bash
./scripts/start-localhost-autorisen.sh 8000 localhost
# Health URL printed by the script: http://localhost:8000/api/health
tail -f /tmp/capecontrol_uvicorn.log
```

Notes:

- **PostgreSQL**: Set `DATABASE_URL=postgresql://vscode:123456@localhost:5432/autorisen_local` in `.env`
- **SQLite Fallback**: The project defaults to SQLite (`DATABASE_URL=sqlite:///./capecontrol.db`) for quick development
- **Database Testing**: Use `./scripts/dummy_register.py` to create test users and verify database connectivity

### Frontend (optional / dev)

The repo supports a local frontend dev server (Vite) with hot-reload. When running with
docker-compose the frontend is mounted for HMR and the backend is available via the
`VITE_API_URL` environment variable (default used for compose is `http://backend:8000`).

```bash
# Run frontend dev server locally
cd client
npm install
npm run dev
# Frontend typically served at http://localhost:3000
```

## CI / CD & Heroku

- GitHub Actions contains a consolidated workflow (`cicd.yml`) that can deploy to Heroku. Historically the project used buildpack-based deploys (push to Heroku git remote) but the CI also supports container-based releases using the Heroku Container Registry.
- The workflow is configured to trigger on pushes to `main` and also contains gated jobs for manual/PR-based container releases (see `.github/workflows/cicd.yml`).

Deployment notes:

- Buildpack (classic) deploys: keep `Procfile`, `requirements.txt` and `runtime.txt` at the repository root so Heroku's Python buildpack can detect and install the backend dependencies. Buildpack deploys use the `Procfile` to start the web process and respect `${PORT}`.
- Container Registry deploys: CI or local deploys may push a container image to `registry.heroku.com/<app>/web` and call `heroku container:release web -a <app>`. When using container deployments the final image must run a web process that binds to the `$PORT` environment variable provided by Heroku.

Current Dockerfile behavior:

- The repository `Dockerfile` contains a multi-stage build. A `release` stage has been added which uses the `backend` stage as the runtime image and starts Gunicorn/Uvicorn bound to `${PORT}`. This makes container releases safe to run on Heroku (prevents the Vite dev server from being started in production images).

Example container release commands (CI or local):

```bash
# Build locally and push to Heroku container registry
docker build -t registry.heroku.com/<app>/web -f Dockerfile .
docker push registry.heroku.com/<app>/web
heroku container:release web -a <app>
```

Important: if you see a Heroku R10 (boot timeout) error, it usually means the container started a process that did not bind to `$PORT` (for example, the Vite dev server on port 3000). Ensure your image's final CMD binds to `${PORT}`.

---

## 5. Database Management

### PostgreSQL Scripts

The project includes automated scripts for database management:

- **`./scripts/setup_local_postgres.sh`**: Automated local PostgreSQL setup
  - Creates local database with production schema
  - Handles SSL connections to Heroku PostgreSQL
  - Updates `.env` configuration automatically
  - Sets up development user permissions

- **`./scripts/dummy_register.py`**: Database testing utility
  - Creates test users for development
  - Validates database connectivity
  - Tests user registration workflow

### Database Connection Details

**Local Development Database:**

- Host: `localhost`
- Port: `5432`
- Database: `autorisen_local`
- Username: `vscode`
- Password: `123456`
- Connection string: `postgresql://vscode:123456@localhost:5432/autorisen_local`

**Production Database:**

- Managed by Heroku PostgreSQL
- SSL required for all connections
- Schema automatically replicated to local environment

### Common Database Commands

```bash
# Connect to local database
PGPASSWORD=123456 psql -h localhost -U vscode -d autorisen_local

# View all tables
\dt

# Describe table structure
\d users_v2

# Check user count
SELECT COUNT(*) FROM users_v2;

# Create test user
python ./scripts/dummy_register.py
```
