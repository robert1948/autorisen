# CapeControl Deployment Environments

## Environment Overview

CapeControl uses a **direct-to-production** deployment strategy:

- **Local Development**: Docker Compose (`docker-compose.yml`) with PostgreSQL, Redis, MinIO
- **Local Integration Tests**: `docker-compose.test.yml` with ephemeral Postgres on port 5434
- **Production**: `capecraft` app → https://cape-control.com

> **Note**: The staging environment (`autorisen` / `dev.cape-control.com`) was retired in March 2026.
> Local Docker with real Postgres provides equivalent integration testing without the operational overhead.

## Database Configuration

### Local Development

```yaml
Database: devdb
Host: localhost:5433
User: devuser
Password: devpass
```

### Local Integration Tests

```yaml
Database: testdb
Host: localhost:5434
User: testuser
Password: testpass
Engine: RAM-backed (tmpfs) — ephemeral, fast
```

### Production (capecraft)

```yaml
Database: d2ggg154krfc75
Cluster: c3nv2ev86aje4j.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com
User: u8h1en29rnu00
Environment: ENV=prod, DEBUG=false
```

## Deployment Process

### Standard Workflow

```text
Local Docker → make codex-test-pg → make deploy ALLOW_PROD=1
```

### Step by Step

```bash
# 1. Build and test locally
make docker-build
make codex-test-pg          # Tests against real Postgres

# 2. Deploy to production (requires ALLOW_PROD=1)
make deploy ALLOW_PROD=1

# 3. Verify production
make smoke-prod
make verify-deploy
```

### Quick Deploy (aliases)

```bash
make deploy-heroku ALLOW_PROD=1   # Alias for make deploy
make ship ALLOW_PROD=1            # Test + build + deploy + verify
```

### Full Release

```bash
make ops-release-all ALLOW_PROD=1
# 1. Sync project plan
# 2. Fix docs lint
# 3. git push origin main
# 4. Deploy to Capecraft
# 5. Release to Docker Hub
```

## Quick Reference Commands

### Environment Info

```bash
# Check production config
heroku config --app capecraft | grep -E "(DATABASE_URL|OPENAI|ENV)"
```

### Logs and Debugging

```bash
# Production logs
heroku logs --tail --app capecraft

# Run commands in production
heroku run --app capecraft "python -c 'print(\"Hello from production\")'"
```

### Health Checks

```bash
# Production health
curl https://cape-control.com/api/health

# Agent health
curl https://cape-control.com/api/agents/cape-ai-guide/health

# Local health
curl http://localhost:8000/api/health
```

## Migration Strategy

When making database changes:

1. Test migrations locally first: `make migrate-up`
2. Test against local Postgres: `make codex-test-pg`
3. Apply to production: `make heroku-run-migrate`
4. Monitor production health: `make smoke-prod`

## Safety Guards

- Production deploys require `ALLOW_PROD=1`
- `scripts/deploy_guard.sh` checks `ALLOW_PROD_DEPLOY=YES` for capecraft
- All push/release commands have 3-attempt retry loops
- Rollback available: `make heroku-rollback REL=vNNN ALLOW_PROD=1`

## Security Notes

- Production uses production-grade security settings (`ENV=prod`, `DEBUG=false`)
- Database credentials are auto-rotated by Heroku PostgreSQL
- All connections use SSL/TLS encryption
- reCAPTCHA enabled in production

---

**Last Updated**: March 2026
**Deployment Version**: v0.2.5+
