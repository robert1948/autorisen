# PLAYBOOK — Release & Deploy (MVP)

## Purpose
Define the authoritative release and deployment guardrails for MVP.
This playbook ensures deployments are controlled, reversible, and do not implicitly
run migrations. It is the operational companion to SYSTEM_SPEC §6.2.

## Spec References
- SYSTEM_SPEC §6.2 (Deployment Rules)
- SYSTEM_SPEC §6.3 (Migration Rules)
- SYSTEM_SPEC §2.6.3 (Migration & Schema Management)
- PLAYBOOK_DB_MIGRATIONS.md (migration procedure — separate from deploy)

---

## 1. Scope

This playbook covers:
- Staging deploys to Heroku app `autorisen` (`dev.cape-control.com`)
- Production deploys to Heroku app `capecraft` (`cape-control.com`)
- Docker Hub image publishing (`stinkie/autorisen`)
- Post-deploy validation and rollback

This playbook does NOT cover:
- Local development (`docker-compose up`)
- Database migrations (see `PLAYBOOK_DB_MIGRATIONS.md`)
- PayFast credential changes (see `PLAYBOOK_NEXT_003_UNBLOCK.md`)

---

## 2. Environments

| Dimension | Staging | Production |
|---|---|---|
| Heroku app | `autorisen` | `capecraft` / `autorisen-dac8e65796e7` |
| Domain | `dev.cape-control.com` | `cape-control.com` |
| GA trigger | Push to `develop` or `staging` | Push to `main` |
| Makefile target | `make deploy-heroku` | `make deploy-capecraft ALLOW_PROD=1` |
| Safety gate | None | `ALLOW_PROD=1` + `deploy_guard.sh` |
| Migrations | Explicit: `make heroku-run-migrate` | Explicit: `make heroku-run-migrate HEROKU_APP_NAME=capecraft` |
| Release phase | **Disabled** — prints warning only | **Disabled** — prints warning only |

---

## 3. Preconditions

Before ANY deployment:

- [ ] The change set is within SYSTEM_SPEC scope (linked to a work order or plan item).
- [ ] CI passes on the branch/PR (backend tests, frontend build, Docker build test).
- [ ] If a migration is involved: it has been approved and tested on staging per
      `PLAYBOOK_DB_MIGRATIONS.md`. Migrations MUST be run separately, never as part of
      the deploy pipeline.
- [ ] Rollback path is understood (revert commit or `heroku rollback`).

Additional preconditions for **production**:
- [ ] The change has been deployed and validated on staging first.
- [ ] `ALLOW_PROD=1` is set intentionally (not by default).
- [ ] No unresolved P0/P1 issues affect the change set.

---

## 4. Allowed Actions

- Execute deployment via approved workflow (GA or Makefile).
- Run post-deploy smoke tests (`make verify-autorisen`, `make smoke-staging`, `make smoke-prod`).
- Publish Docker Hub images via `make dockerhub-release` or manual GA trigger.
- Execute `make certify-autorisen` for formal release certification.

---

## 5. Explicit Stop Conditions

- **STOP** if the deploy would include implicit migrations (release phase is disabled for
  this reason — verify it remains so).
- **STOP** if rollback is not feasible or not documented.
- **STOP** if required CI checks have not passed.
- **STOP** if a production deploy is attempted without staging validation first.
- **STOP** if `deploy_guard.sh` or `require-prod` rejects the operation.

---

## 6. Deployment Procedures

### 6.1 Staging Deploy (Automated)

**Trigger:** Push to `develop` or `staging` branch.

**What happens automatically** (via `deploy-staging.yml`):
1. `test-before-deploy` job runs `make codex-test`.
2. Heroku CLI installed, Docker image built with `NODE_ENV=staging`.
3. Image pushed to `registry.heroku.com/autorisen/web`.
4. `heroku container:release web -a autorisen` executed.
5. Alembic migrations run explicitly (in workflow, not release phase).
6. Smoke test: `/api/health` and `/api/auth/csrf` verified.

**Manual alternative:**
```bash
make deploy-heroku              # push + release to autorisen
make verify-autorisen           # check releases, version, DB
make smoke-staging              # health + CSRF probe
```

### 6.2 Production Deploy (Automated)

**Trigger:** Push to `main` branch.

**What happens automatically** (via `deploy-heroku.yml`):
1. Checkout + plan validation (`make plan-sync`).
2. Heroku CLI installed, Docker image built with `NODE_ENV=production, ENV=prod`.
3. Image structure verified (non-root user, required dirs exist).
4. Image pushed to `registry.heroku.com/autorisen-dac8e65796e7/web`.
5. `heroku container:release web -a autorisen-dac8e65796e7` executed.
6. Alembic migrations run explicitly (in workflow, not release phase).
7. Health check with 5 retries (30s waits), CSRF endpoint check, version check.

**Manual alternative:**
```bash
make deploy-capecraft ALLOW_PROD=1     # requires safety gate
make smoke-prod                        # health check
```

### 6.3 Docker Hub Publish

**Trigger:** Manual via GitHub Actions (`workflow_dispatch`) or Makefile.

```bash
make dockerhub-release                 # multi-arch buildx + push
# Tags: :v0.2.10, :latest, :docker-<engine>, :git-<sha>
```

Or trigger `dockerhub-publish.yml` manually from GitHub Actions tab.

### 6.4 Full Ship Pipeline

For a complete staging release with evidence:
```bash
make ship-autorisen-log
# Runs: test-backend → build-client → deploy-autorisen → verify-autorisen
# Output: timestamped evidence log in ship_autorisen_*.log
```

For formal certification:
```bash
make certify-autorisen
# Runs: 2x idempotent migrations, health+smoke, version SHA match,
#        log scan for traceback/5xx, writes .release/autorisen_certified
```

---

## 7. Post-Deploy Validation

### Required checks (all environments)

| Check | Command | Pass criteria |
|---|---|---|
| Health | `curl /api/health` | HTTP 200, `status: healthy` |
| CSRF | `curl /api/auth/csrf` | HTTP 200, sets `csrf_token` cookie |
| Version | `curl /api/version` | Returns current `GIT_SHA` |

### Additional staging checks

| Check | Command | Pass criteria |
|---|---|---|
| Verify releases | `make verify-autorisen` | Latest release matches expected SHA |
| DB version | `heroku pg:psql -c "SELECT version_num FROM alembic_version"` | Expected revision |
| Smoke | `make smoke-staging` | Health + CSRF probe pass |

---

## 8. Rollback Procedure

### Staging rollback
```bash
heroku rollback -a autorisen
# Or: revert the merge commit on develop/staging, push → auto-redeploy
```

### Production rollback
```bash
make heroku-rollback REL=vNNN ALLOW_PROD=1
# REL = the release number to roll back to (from heroku releases -a capecraft)
```

### Database rollback
If the deploy included a migration that needs reversal:
- Follow `PLAYBOOK_DB_MIGRATIONS.md` rollback procedure.
- Run `alembic downgrade <previous-revision>` explicitly.
- **Never** rely on release-phase rollback (it is disabled).

### When rollback is NOT sufficient
- If the deploy changed database schema in a non-reversible way (data loss, dropped columns).
- If the deploy changed external service configuration (PayFast, OAuth providers).
- In these cases: manual remediation is required. Document the incident.

---

## 9. Safety Mechanisms Summary

| Mechanism | Purpose |
|---|---|
| `ALLOW_PROD=0` default | Prevents accidental production deploys |
| `deploy_guard.sh` | Blocks capecraft deploys without `ALLOW_PROD_DEPLOY=YES` |
| Release-phase disabled | No implicit migrations in Procfile or heroku.yml |
| 3-attempt retry loops | Handles transient Heroku API failures |
| `certify-autorisen` | Formal certification with evidence file |
| `ship-autorisen-log` | Evidence capture to timestamped logs |
| CI gate | Tests must pass before deploy workflows proceed |

---

## 10. Audit Trail

All deployments should be traceable:
- GitHub Actions run logs (linked from PR or commit).
- `make ship-autorisen-log` output (when used).
- `.release/autorisen_certified` file (when `certify-autorisen` used).
- Heroku release history: `heroku releases -a <app>`.
- `docs/evidence/<WO-ID>/` directory for work-order-linked deploys.
