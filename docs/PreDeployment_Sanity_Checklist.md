# docs/PreDeployment\_Sanity\_Checklist.md

> **Purpose**: Repeatable pre‑deployment sanity & health checks for the CapeControl stack (FastAPI + React + Postgres + Docker + Heroku). Use this prior to any promotion to production.

## 0) Gatekeeping (stop if any ❌)

* [ ] All sections below are ✅
* [ ] Release notes & version tag prepared (e.g., `v###`)
* [ ] Rollback plan verified (previous release runnable + DB backup available)

---

## 1) Repo & Branch Hygiene

* [ ] On correct branch (`main`/`release/*`) and up to date
* [ ] Working tree clean (no uncommitted files)
* [ ] Changelog updated / Conventional Commits
* [ ] No accidental large/binary files committed

**Quick cmds**

```bash
git fetch --all --prune
git status
git log --oneline -n 10
```

---

## 2) Code Quality (Backend & Frontend)

* [ ] Lint passes (Python: ruff; JS: eslint)
* [ ] Static typing passes (mypy / TS where applicable)
* [ ] Unit tests pass locally
* [ ] Coverage ≥ 80% (or team target)
* [ ] No TODO/FIXME in critical paths

**Quick cmds**

```bash
# Python
ruff check .
mypy backend/src
pytest -q --maxfail=1 --disable-warnings --cov=backend/src

# JS/React
cd client && npm run lint && npm test -- --watch=false
```

---

## 3) Dependencies & Supply Chain

* [ ] Locked & reproducible (Python `requirements*.txt`; Node `package-lock.json`)
* [ ] No known critical vulns (Python: safety; Node: npm audit)
* [ ] Pin key versions; runtime saved (`runtime.txt` if using buildpacks)

**Quick cmds**

```bash
pip install -r backend/requirements.txt
pip list --outdated
safety check --full-report || true

cd client
npm ci
npm audit --omit=dev
```

---

## 4) Security & Secrets

* [ ] Secrets only in env (no hard‑coded creds)
* [ ] JWT/CSRF/session settings set for PROD
* [ ] CORS/ALLOWED\_HOSTS/HTTPS enforced
* [ ] API keys (OpenAI, Payfast, etc.) set for correct env
* [ ] Admin routes locked; rate limiting active

**Quick cmds**

```bash
# Spot-check for accidental secrets in repo
git secrets --scan || true
```

---

## 5) Configuration Parity (Dev ↔ Staging ↔ Prod)

* [ ] `.env.example` complete and current
* [ ] Staging mirrors prod config (except secrets)
* [ ] Feature flags correct for target environment

**Heroku spot‑checks**

```bash
heroku config -a <app-name>
heroku releases -a <app-name>
```

---

## 6) Database & Migrations

* [ ] Migrations generated, reviewed, applied in staging
* [ ] Backups taken (and restorable)
* [ ] No destructive ops without fallback
* [ ] Seeds/fixtures idempotent

**Quick cmds**

```bash
alembic upgrade head

# Heroku Postgres
heroku pg:backups:capture -a <app>
heroku pg:backups:download -a <app> # (optionally test restore locally)
```

---

## 7) Build & Artifact Integrity

* [ ] Backend builds (Docker/buildpack)
* [ ] Frontend builds (no type errors; optimized size)
* [ ] Static assets/S3 sync (if applicable)

**Quick cmds**

```bash
# Docker
docker build -t <image>:candidate .
docker run --rm -p 8000:8000 <image>:candidate

# React
cd client && npm run build
```

---

## 8) Runtime Health (Local/Staging)

* [ ] App boots cleanly (no startup errors)
* [ ] Health endpoints pass (`/health`, `/metrics`)
* [ ] Key flows manual smoke‑tested (login, onboarding, payments, critical APIs)
* [ ] Logs clean (no unhandled exceptions/warning spam)

**Quick cmds**

```bash
curl -fsS http://localhost:8000/health
heroku logs -a <staging-app> --tail
```

---

## 9) CI/CD Status

* [ ] All pipelines green (lint, type, tests, build, image)
* [ ] Required checks enforced on merge to `main`
* [ ] Release job uses immutable refs (tags/digests)
* [ ] Artifact provenance recorded (commit SHA, build ID)

---

## 10) Observability & Guardrails

* [ ] Monitoring dashboards up (CPU, mem, latency, error rate)
* [ ] Alerts configured (error spikes, p95 latency, DB connections)
* [ ] Error tracking DSNs live; release tagging active
* [ ] Rate limiting / DDoS / input sanitization enabled

---

## 11) Performance & UX Sanity

* [ ] API latency within target (staging)
* [ ] Lighthouse: Performance/Accessibility/Best‑Practices/SEO ≥ team target
* [ ] Images compressed; no blocking requests; sane cache headers

---

## 12) Compliance & Content

* [ ] Privacy policy/ToS links present
* [ ] Cookie consent (if required)
* [ ] Contact/support details visible
* [ ] Pricing/legal copy updated

---

## 13) Release & Rollback Readiness

* [ ] Version bump committed & tagged
* [ ] Release notes summarize scope & risks
* [ ] Rollback command tested (prior image/release known‑good)
* [ ] DB rollback plan (or backward‑compatible migrations)

**Heroku examples**

```bash
# Promote staging → prod (pipelines)
heroku pipelines:promote -a <staging-app>

# Rollback
eroku releases:rollback vNN -a <prod-app>
```

---

## 14) Final Sign‑off

* [ ] Tech lead ✅
* [ ] QA ✅
* [ ] Product/Owner ✅

**Notes / Deviations**

```
- …
```

---

# .github/workflows/predeploy-gate.yml (GitHub Actions)

```yaml
name: predeploy-gate

on:
  pull_request:
    branches: ["main"]
  workflow_dispatch: {}

permissions:
  contents: read

jobs:
  gate:
    name: Pre‑Deployment Sanity Gate
    runs-on: ubuntu-latest

    env:
      PYTHONDONTWRITEBYTECODE: "1"
      PIP_DISABLE_PIP_VERSION_CHECK: "1"
      UV_SYSTEM_PYTHON: "1"

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install backend deps
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          # Optional: separate dev requirements if present
          if [ -f backend/requirements-dev.txt ]; then pip install -r backend/requirements-dev.txt; fi

      - name: Backend lint (ruff)
        run: |
          ruff --version || pip install ruff
          ruff check .

      - name: Backend typing (mypy)
        run: |
          mypy --version || pip install mypy
          mypy backend/src

      - name: Backend tests (pytest + coverage)
        run: |
          pip install pytest pytest-cov
          pytest -q --maxfail=1 --disable-warnings --cov=backend/src --cov-report=term-missing

      - name: Supply chain (safety)
        run: |
          pip install safety
          # Non-fatal for PRs; fail only on HIGH/CRITICAL if you prefer
          safety check --full-report || true

      - name: Set up Node 20
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: client/package-lock.json

      - name: Install frontend deps (npm ci)
        working-directory: client
        run: npm ci

      - name: Frontend lint (eslint)
        working-directory: client
        run: |
          if npm run | grep -q " lint"; then npm run lint; else echo "no lint script"; fi

      - name: Frontend tests (jest)
        working-directory: client
        run: |
          if npm run | grep -q " test"; then npm test -- --watch=false; else echo "no test script"; fi

      - name: Frontend build
        working-directory: client
        run: |
          if npm run | grep -q " build"; then npm run build; else echo "no build script"; fi

      - name: Record artifact provenance
        run: |
          echo "GIT_SHA=$(git rev-parse HEAD)" >> $GITHUB_ENV
          echo "GIT_SHORT_SHA=$(git rev-parse --short HEAD)" >> $GITHUB_ENV

      - name: Summary
        run: |
          echo "✅ Pre‑deployment gate passed for $GITHUB_SHA" >> $GITHUB_STEP_SUMMARY
          echo "Commit: ${GIT_SHORT_SHA}" >> $GITHUB_STEP_SUMMARY

```

## How to enable as a required gate

1. Commit this file to `.github/workflows/predeploy-gate.yml` and the checklist to `docs/PreDeployment_Sanity_Checklist.md`.
2. In GitHub → **Settings → Branches → Branch protection rules** for `main`:

   * Require a pull request before merging
   * Require status checks to pass before merging
   * Select **predeploy-gate** as a required status check
   * (Optional) Require approvals (e.g., 1‑2 reviewers)
3. Merge PRs only after this workflow is ✅.

## Optional extensions

* Add Lighthouse CI job against staging URL (requires project token; runs headless Chrome)
* Upload coverage report as artifact and enforce a minimum (%)
* Add SAST (CodeQL) & dependency review
* Add Docker build test (`docker build` + Trivy scan)
* Add API contract tests (e.g., Schemathesis) against a local ephemeral app

