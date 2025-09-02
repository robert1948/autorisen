# Autorisen — Heroku Container Predeploy Gate Pack

This pack replaces the GitHub Actions–based gate with a **local gate** and **Makefile** tailored for Heroku Container Registry deploys.

## Files
- `scripts/predeploy_gate.sh` — run all predeploy checks locally (docs delta, Python import sanity, tests, optional frontend build, optional Alembic).
- `Makefile` — convenience targets for `predeploy` and Heroku Container (`heroku-deploy`, `heroku-logs`, etc.).
- `docs/PreDeployment_Policy_Checklist.md` — the human checklist.
- `.githooks/pre-push` — optional local Git hook to run the gate on `git push`.

## Install
Copy these into your repo root, preserving paths. Then:
```bash
# activate venv first
source .venv/bin/activate

# optional: use local hooks so the gate runs on 'git push'
git config core.hooksPath .githooks
```

## Use
```bash
# Run the gate before deploying
make predeploy

# Deploy with Heroku Container
HEROKU_APP=autorisen make heroku-deploy

# Tail logs
make heroku-logs

# Quick smoke test
make smoke
```
