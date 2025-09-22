# 🛠 DEVELOPMENT CONTEXT

Last updated: 2025-08-27

This file is the concise, canonical quickstart for running the project locally. The full historic content is preserved in `docs/DEVELOPMENT_CONTEXT.md.bak`.

## Quick start

```bash
# Start the development stack (build + detached)
make dev-up

# Run DB migrations inside the backend container
make migrate

# Run quick health checks (backend, DB, frontend)
make smoke
```

## Ports (authoritative)

- Frontend (Vite): `http://localhost:3000` — Docker Compose maps the frontend container's Vite port `5173` to host port `3000` (container internal `5173`, host `3000`).
- Backend (Uvicorn): `http://localhost:8000` (health: `/api/health`).
- Postgres (host): `localhost:5433` (if using the Compose-provided DB).

Notes

- If you run the frontend dev server directly on your host (not via Compose), Vite's default dev server uses port `5173`.
- Keep Heroku settings unchanged in this repo unless you have explicit permission to modify the Heroku app(s).
- For full historical context and extra troubleshooting notes, open `docs/DEVELOPMENT_CONTEXT.md.bak`.
<!-- Archived historical content moved to docs/DEVELOPMENT_CONTEXT.md.bak -->
<!-- For the full historical document, executive summary, company information, and extended setup instructions, see docs/DEVELOPMENT_CONTEXT.md.bak -->

## Development Workflow

## Component Source Management

- **Source Repository**: If any components are missing from the autorisen project, they should be copied from **capecraft production environment** (Heroku)
- **Development Priority**: The autorisen project must always be ahead of capecraft in development lifecycle

## Deployment Pipeline Strategy

1. **Development Phase**: Build and test all functionality on autorisen first
2. **Testing Phase**: Ensure complete functionality validation before promotion
3. **Production Deployment**: Push to capecraft (live site) only after thorough testing
4. **Service Continuity**: Maintain zero disruption to live services
5. **Uptime Requirements**: Ensure absolute minimal downtime during deployments

## Quality Assurance Protocol

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

### Frontend (optional)

```bash
cd client
npm install
npm run dev
# Frontend typically served at http://localhost:3000
```

### CI / CD & Heroku

- GitHub Actions contains a consolidated workflow (`cicd.yml`) that builds and deploys to Heroku using buildpack-based deployment (not container-based).
- The workflow is configured to trigger on pushes to `main` and supports manual promotion to production via workflow_dispatch.
- Staging deploys are achieved by pushing the contents of `backend/` (with `Procfile`, `requirements.txt`, and `runtime.txt` at root) to the Heroku git remote.
- If you prefer staging-only deploys from a feature branch, update the workflow to trigger only on that branch and use manual promotion from `main` for production.

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
