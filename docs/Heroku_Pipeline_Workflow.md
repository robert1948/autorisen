# 🧭 Heroku Pipeline Workflow — *AutoLocal / CapeControl*

This document describes how our containerized **FastAPI + React** stack is built, tested, and deployed through **Heroku** using both the `Makefile` and GitHub Actions.

---

## 🚀 Environments

| Stage | Heroku App | URL | Purpose |
|-------|-------------|-----|----------|
| **Local** | Docker Compose | `http://localhost:8000` / `http://localhost:3000` | Development & tests |
| **Staging** | `autorisen` | <https://dev.cape-control.com> | Continuous Integration & QA |
| **Production** | `capecraft` (planned) | <https://cape-control.com> | Public release |

---

## 🧪 Continuous Integration (GitHub Actions)

| Workflow | Path | Purpose |
|-----------|------|----------|
| **CI – Tests** | `.github/workflows/ci-test.yml` | Runs `pytest -q` with SQLite, uploads coverage XML |
| **Deploy – Staging** | `.github/workflows/deploy-staging.yml` | Builds Docker image → pushes to Heroku → releases → runs Alembic migrations → smoke-tests `/api/health` |

### CI Secrets (set in GitHub → *Settings → Secrets and variables*)

| Name | Description |
|------|-------------|
| `HEROKU_API_KEY` | Token from `heroku auth:token` |
| *(optional)* `EMAIL_TOKEN_SECRET`, `SMTP_USERNAME`, etc. | For staging email tests if needed |

---

## 🧰 Local Deployment Flow

### 1️⃣ Prepare

```bash
# ensure env
export HEROKU_APP_NAME=autorisen
heroku container:login
