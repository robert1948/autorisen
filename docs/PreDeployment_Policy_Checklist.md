# 🚀 Pre-Deployment Policy & Checklist

**Repo:** `autorisen`  
**Purpose:** Ensure localhost-first development, keep documentation up to date, and only update **Capecraft (PRODUCTION)** when **Autorisen** is ahead and fully functional.

---

## 1) Local Development & Simulation
- [ ] Pull latest `main`.
- [ ] Run backend locally: `export PYTHONPATH=backend && uvicorn app.main:app --reload --port 8000`.
- [ ] Open API docs: `http://localhost:8000/docs`.
- [ ] (Optional) Run client `cd client && npm install && npm run dev` and verify it talks to API.
- [ ] Migrations run cleanly (Alembic or your tool of choice).
- [ ] Smoke tests pass: `pytest -q` or `make test`.

## 2) Documentation Updates
- [ ] Update `docs/LOCAL_DEVELOPMENT_AND_HEROKU.md` for any config/ENV changes.
- [ ] Update this checklist if the process changed.
- [ ] Add new endpoints/deps/migrations to docs.
- [ ] Commit docs changes **before** pushing deployment code.

## 3) Deploy to Autorisen (Staging via Heroku Container)
- [ ] Run `make predeploy` (runs this gate script).
- [ ] Run `make heroku-deploy` to push & release the container to Heroku app `autorisen` (or set `HEROKU_APP=...`).
- [ ] Tail logs: `make heroku-logs`.
- [ ] Verify `/api/health` and API docs.
- [ ] Run smoke tests against Autorisen.

## 4) Functional Verification
- [ ] Critical routes respond correctly.
- [ ] Auth & onboarding flows OK.
- [ ] DB migrations completed on Heroku PG.
- [ ] Third-party integrations (Stripe/S3/etc.) OK.
- [ ] Error/perf logs show no regressions.

## 5) Capecraft (Production) Update Policy
- [ ] ✅ Autorisen is fully functional.
- [ ] ✅ Autorisen is **ahead of** Capecraft.
- [ ] ✅ Documentation updated & committed.
- [ ] Then (and only then) update **Capecraft (PRODUCTION)** from Autorisen.
- [ ] Repeat verification post-deploy.

## 6) Post-Deployment
- [ ] Tag the release in Git: `git tag -a vX.Y.Z -m "notes" && git push --tags`.
- [ ] Update `CHANGELOG.md`.
- [ ] Notify the team & update runbooks/trackers.
