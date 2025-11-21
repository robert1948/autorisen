# AutoLocal/CapeControl AI Coding Instructions

## Architecture Overview

This is a **production-ready FastAPI + React SaaS platform** deployed as containers to Heroku. The system implements a modular agent-based architecture where business logic is organized into specialized agents that handle specific domains (auth, monitoring, audit, etc.).

**Current Version:** v0.2.5 (November 2025)

### Key Structural Patterns

- **Dual App Structure**: Both `app/main.py` (shim fallback) and `backend/src/app.py` (main factory) exist for import flexibility
- **Agent-Centric Design**: Business logic organized in `backend/src/modules/*/` as domain agents (auth, chatkit, flows, marketplace)
- **Environment Cascade**: Settings load from `.env` → environment vars → Pydantic defaults with validation
- **Container-First Deployment**: Multi-stage Docker builds with Heroku Container Registry for staging/production
- **Quality Automation**: Comprehensive CI/CD with GitHub Actions, automated linting, and security scanning

## Critical Development Workflows

### Essential Make Targets

```bash
make install        # Bootstrap Python venv + dependencies
make project-info   # Print live roadmap stats from docs/project-plan.csv
make codex-test     # CI-safe pytest with test database isolation
make docker-build   # Build autorisen:local with retries
make deploy-heroku  # Full build → push → release to Heroku (with retry logic)
make heroku-logs    # Live log tailing
```

### Environment Configuration

- **Local**: `docker-compose.yml` with PostgreSQL on `:5433`, Redis `:6379`, Vite dev server `:5173`
- **Staging**: `autorisen` Heroku app (`https://dev.cape-control.com`)
- **Production**: Live at `https://autorisen-dac8e65796e7.herokuapp.com`

### Database Patterns

- **Migration Path**: Alembic with auto-upgrade disabled (`RUN_DB_MIGRATIONS_ON_STARTUP=0` in production)
- **Test Isolation**: Uses `sqlite:////tmp/autolocal_test.db` with environment variable overrides
- **Connection Settings**: Pydantic `Settings` class in `backend/src/core/config.py` with legacy name compatibility

## Project-Specific Conventions

### Module Organization

- **Router Pattern**: Each module has a `router.py` that gets safely imported by the app factory
- **Safe Import Strategy**: App factory uses try/catch imports with logging for missing modules
- **Middleware Integration**: Custom middleware in `backend/src/middleware/` with agent delegation

### Authentication Architecture

- **JWT + CSRF**: Dual-token system with refresh cookies and CSRF protection
- **Production Hardening**: `ENV=prod`, `DEBUG=false`, reCAPTCHA enabled in production
- **OAuth Support**: Google/LinkedIn integration with shared callback handling

### Agent Development Pattern

```python
# Standard agent structure in backend/src/modules/{domain}/
router.py         # FastAPI router with endpoints
models.py         # Pydantic request/response models
service.py        # Business logic implementation
```

### Testing Strategy

- **Enabled Tests**: Only `tests_enabled/` directory runs in CI (via `pytest.ini`)
- **Fixture Healing**: `scripts/regenerate_fixtures.py` auto-repairs broken test data
- **Environment Isolation**: Tests use separate SQLite database with full environment override

## Integration Points & External Dependencies

### Heroku Container Deployment

- **Registry Flow**: `docker build` → `heroku container:push web` → `heroku container:release web`
- **Retry Logic**: All deployment commands include 3-attempt retry loops for transient failures
- **Health Validation**: Post-deploy verification via `/api/health` and `/api/auth/csrf`

### Frontend Build Integration

- **Vite + React**: TypeScript client with Tailwind, builds to `client/dist/`
- **Asset Strategy**: Favicons/PWA icons managed via build process, served as static files
- **API Proxy**: Vite dev server proxies `/api/*` to backend during development

### Monitoring & Operations

- **Health Endpoints**: `/api/health` (with DB check), `/api/version`, `/api/security/stats`
- **Audit Trail**: Request logging via `AuditLoggingMiddleware` → `AuditAgent`
- **Security Stack**: DDoS protection, input sanitization, rate limiting with Redis backend

### Roadmap & Planning

- `docs/project-plan.csv` is the authoritative backlog; update it first, then run `python scripts/plan_sync.py --apply` to refresh `docs/Master_ProjectPlan.md`.
- `make project-info` summarizes live task/hour totals directly from the CSV so CLI output matches the plan snapshot.

## Key Files to Understand

- `Makefile`: Single source of truth for all development/deployment commands
- `backend/src/app.py`: Main application factory with safe router imports
- `backend/src/core/config.py`: Environment configuration with Pydantic validation
- `docker-compose.yml`: Local development stack definition
- `docs/agents.md`: Current agent registry and status
- `pytest.ini`: Test configuration (only runs `tests_enabled/`)

## Common Debugging Approaches

- **Failed Deployments**: Check `make heroku-logs` for container startup issues
- **Import Errors**: App factory gracefully handles missing modules - check logs for which routers failed to load
- **Test Failures**: Use `make codex-test-heal` to regenerate fixtures before investigating
- **Database Issues**: Verify `DATABASE_URL` format and check if manual migration needed via `make heroku-run-migrate`

When modifying this codebase, always test locally with `make docker-build && make docker-run` before deploying, and ensure any new modules follow the safe import pattern used in the app factory.
