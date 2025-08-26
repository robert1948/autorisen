# 🚀 Integration Plan — Autorisen → CapeControl

**Last Updated**: August 23, 2025  
**Aligned with**: `DEVELOPMENT_CONTEXT.md` (CapeControl / Capecraft v663)

---

## 1. Context

We are integrating `autorisen` features into the CapeControl / Capecraft production app (`capecraft`, currently **v663** on Heroku). Both projects use **FastAPI 0.110.0 + Python 3.12 + PostgreSQL** with React 18 on the frontend.  
The plan ensures a **safe, feature-flagged rollout** with additive DB migrations, contract testing, and observability. Heroku now uses buildpack-based deployment (Procfile, requirements.txt, runtime.txt at backend root).

---

## 2. Constraints (from DEVELOPMENT_CONTEXT.md)

- **Production**: Heroku app `capecraft` v663.
- **Staging**: `autorisen` repo, used for feature validation.
- **Security**:
  - Input Sanitization ✅
  - Audit Logging ✅
  - DDoS Protection / AI Rate Limiting ✅
  - Content Moderation ⚠️ Disabled in production
- **Payments**: Stripe integration deployed, pinned at `stripe==7.7.0`.
- **Static Assets**: Served from `/app/app/static`.
- **Known Issues**:
  - Pydantic warning (`model_used`) — must rename or adjust config.
  - SendGrid not configured — SMTP fallback in place.
- **Monitoring**: Heroku metrics, AI performance sampler, Sentry error tracking, audit alerts.
- **Performance Snapshot (prod)**: CPU 3.8–22.7%, Memory ~41.8–41.9%, p95 latency <100ms.

---

## 3. Checklist (requirements coverage)

- [ ] Additive Alembic migrations + DB snapshot/backup before prod
- [ ] API inventory + OpenAPI diff for breaking changes
- [ ] Namespaced routes under `/api/autorisen/*` behind `FEATURE_AUTORISEN`
- [ ] Shared auth module + JWT/RBAC contract tests
- [ ] CI import-sanity + schema diff checks
- [ ] Backfill scripts + verification on staging
- [ ] Observability dashboards (CPU, memory, latency, 5xx errors, auth fails)
- [ ] Release runbook with backup, deploy, verify, rollback

---

## 4. 48–72h Plan (Tasks, Owners, Commands)

### 1. API Inventory & Diff — **Backend** (Day 1)

Export OpenAPI specs from both projects and produce diff:

```bash
# CapeControl spec
PYTHONPATH=backend uvicorn app.main:app --port 8001 &
curl -s http://127.0.0.1:8001/openapi.json > /tmp/capecontrol.json

# Autorisen spec (canonical backend FastAPI app)
PYTHONPATH=backend python -c "import json; from app import main as m; print(json.dumps(m.app.openapi()))" > /tmp/autorisen.json
```
