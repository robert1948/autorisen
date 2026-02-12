# WO-OPS-REPO-HYGIENE-001 Summary

## What changed
- SSOT cleanup + row insertion in docs/project-plan.csv.
- Added docs/REPO_HYGIENE.md.
- Updated .gitignore for caches, artifacts, and evidence raw paths.
- Added scripts/clean.sh and scripts/audit_repo_size.sh.
- Updated client/pnpm-lock.yaml after lockfile drift.

## Size highlights (before -> after)
- Total size: 626M -> 294M.
- Removed heavy local artifacts:
  - .venv (180M) removed.
  - client/node_modules (148M) removed.
  - client/dist (3.3M) removed.

## Cleanup actions
- git clean -fdX
- git clean -fd -e docs/evidence

## Verification results
- pytest (initial): failed due to missing email-validator, semver, and pytest in venv.
- Dependencies: venv rebuilt; backend/requirements.txt + requirements-dev.txt installed; imports OK.
- pytest (final): pass.
- Frontend: pnpm-lock.yaml was out-of-date; updated via pnpm install --no-frozen-lockfile; build succeeded; frozen reinstall succeeded.
- Docker compose build: succeeded.

## Safety note
- Autorisen-only; no capecraft/prod deploys performed.
