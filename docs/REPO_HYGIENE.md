# CapeControl Repo Hygiene

> Task: WO-OPS-REPO-HYGIENE-001 | Updated: 2026-02-19

## Purpose

Keep the autorisen repo lean, auditable, and CI-friendly.
This document records the repo hygiene policy and actions taken.

---

## 1. What stays in Git

- Source code, configs, Dockerfiles, compose files
- Docs, specs, and runbooks
- Evidence packs (copy/paste-ready summaries, logs, small diffs)
- Authoritative project plan (`docs/project-plan.csv`, `docs/Master_ProjectPlan.md`)

## 2. What must NOT be committed

- Build artifacts: `node_modules/`, `dist/`, `build/`, `.vite/`
- Python caches/venvs: `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.venv/`
- Logs and runtime output: `*.log`, `logs/`, `tmp/`
- Secrets: `.env`, keys, tokens, credentials
- Heavy/raw evidence: screenshots, videos, HAR files, DB dumps

---

## 3. .gitignore

**Status:** Consolidated (2026-02-19)

| Metric | Before | After |
|--------|--------|-------|
| Lines | 408 | 315 |
| Duplicate entries | 37 | 0 |

Organised into labelled sections: Python, Node, Secrets, IDE/OS, Databases, Build/Deploy, Logs/Temp, Testing, Media, Dev artifacts, Evidence policy.

---

## 4. Cleanup Script

**Path:** `scripts/clean.sh`

```bash
./scripts/clean.sh              # Default: Python + Node caches
./scripts/clean.sh --dry-run    # Preview only
./scripts/clean.sh --branches   # Also prune stale merged branches
./scripts/clean.sh --all        # Everything
```

The script never deletes tracked files or `node_modules` (expensive to reinstall).

---

## 5. Evidence Policy

Evidence packs live under `docs/evidence/<TASK-ID>/`.

**Tracked:** Log files, verification summaries, small patches (< 200 KB).
**Ignored:** Raw screenshots, video, HAR files, DB dumps, `docs/evidence/_raw/`.

---

## 6. Stale Branches

16 merged branches cleaned (2026-02-19). All had been merged into `main`.
Use `./scripts/clean.sh --branches` to prune future merged branches.

---

## 7. Repo Size Breakdown

| Directory | Size | Notes |
|-----------|------|-------|
| `.git/` | 291 MB | History; run `git gc --aggressive` periodically |
| `.venv/` | 196 MB | Ignored; local only |
| `client/node_modules/` | 157 MB | Ignored; local only |
| `client/src/` | 1.7 MB | Source |
| `docs/` | 4.1 MB | Documentation + evidence |
| `backend/` | 2.9 MB | Backend source |
| **Total** | **~659 MB** | Tracked content is lean |

---

## 8. Maintenance Schedule

- **Per session:** `./scripts/clean.sh --dry-run` before commits
- **Weekly:** `./scripts/clean.sh --all` to prune branches
- **Monthly:** `git gc --aggressive` if .git exceeds 300 MB
- **On PR merge:** Delete feature branch (GitHub auto-delete recommended)

## Safety

This repo is staging/sandbox (autorisen). Do not run production/capecraft commands unless explicitly instructed by Robert.
