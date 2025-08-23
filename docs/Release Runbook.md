Release runbook

# 🚀 CapeControl Release Runbook

**Last Updated**: August 23, 2025  
**Applies to**: CapeControl / Capecraft Production App (`capecraft`, Heroku v663)  
**Primary Reference**: `DEVELOPMENT_CONTEXT.md`
**See also**: `docs/Integration Plan.md`

---

## 1. Pre-Release Checklist ✅

- [ ] All tests pass locally and in CI (unit, integration, e2e).
- [ ] API diff checked (`/openapi.json` vs staging).
- [ ] Alembic migrations are **additive only** and verified on staging.
- [ ] `DEVELOPMENT_CONTEXT.md` updated with new version + notes.
- [ ] Feature flags prepared (e.g., `FEATURE_AUTORISEN`).
- [ ] Observability dashboards reviewed (CPU, memory, latency, error rate).

---

## 2. Backup 🗄️

**Database Snapshot (Heroku Postgres)**

```bash
heroku pg:backups:capture -a capecraft
heroku pg:backups:download -a capecraft
```
