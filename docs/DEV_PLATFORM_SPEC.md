# DEV_PLATFORM_SPEC.md
# CapeControl Development Platform Spec (autorisen-only)

## 0) Purpose
This document defines the operating rules for implementing work orders (WOs) in the CapeControl repository. It is designed for agentic execution (Codex) with strong governance, predictable outputs, and auditable evidence.

## 1) Authority Chain (must be honored)
**Robert (final authority) → CapeAI (planning/governance) → VS_Chat (manager/orchestrator) → Codex (worker/implementer)**

- Robert is the only entity that can authorize production deploy/release.
- VS_Chat issues WOs and validates evidence.
- Codex executes WOs end-to-end and returns an evidence pack.

## 2) Environments and Non-Negotiable Guardrails
### 2.1 Staging only
- **Allowed Heroku app:** `autorisen` (staging/sandbox only)
- **Forbidden Heroku app:** `capecraft` (production)

### 2.2 No production deploy/release
- **DO NOT** deploy/release to production (`capecraft`) unless Robert explicitly instructs it in the WO.
- If any instruction ambiguously implies production, STOP and ask for clarification.

### 2.3 No destructive / risky operations without explicit WO permission
Unless the WO explicitly includes it, do **not** perform:
- DB migrations, schema changes, or Alembic revisions
- Dropping tables, truncation, bulk deletes
- Secret rotation / environment variable changes
- Package lockfile churn / dependency upgrades
- Broad refactors outside scope
- Any action that touches production resources

## 3) Repo Scope and Working Directory
- Repo root (canonical): `/home/robert/Development/capecontrol`
- All work must remain inside this repo unless the WO explicitly extends scope.

## 4) Operating Mode (how Codex should behave)
### 4.1 Default behavior: execute end-to-end without pausing
Codex should proceed autonomously within this spec:
- Perform discovery (ripgrep, open files)
- Implement changes limited to WO scope
- Run verification commands
- Produce evidence pack
- Commit once (unless WO requires multiple commits)

### 4.2 When to STOP and ask (hard stop)
Stop and ask only if:
- The WO conflicts with guardrails (prod, migrations, secrets, destructive ops)
- Acceptance criteria are ambiguous or contradictory
- Required files/paths do not exist
- Verification fails and the fix requires expanding scope beyond the WO

## 5) Command Policy (reduce “it keeps stopping”)
### 5.1 Pre-approved local commands (no ask)
- Git: `git status`, `git branch`, `git log`, `git diff`, `git show`, `git add`, `git commit`, `git mv`, `git restore`, `git checkout -b/-B`, `git pull --rebase`, `git push`
- Search/inspect: `rg`, `ls`, `cat`, `sed -n`, `awk`, `tail`, `head`
- Python: `pytest`, `python -m pytest`, `ruff`, `uv` (if already present), venv python
- Node: `npm -C client run build`, `npm -C client test` (or repo-defined test scripts)
- Docker local: `docker compose up/down/build/logs` (read-only logs ok)
- Curl checks to staging URLs are allowed

### 5.2 Ask-first commands (must ask unless WO explicitly authorizes)
- Anything that changes environment variables on Heroku
- Any migration commands (`alembic`, `manage.py migrate`, etc.)
- Dependency upgrades (`npm install`, `pip install`, lockfile regeneration) unless explicitly required
- `rm -rf`, mass deletes, rewriting git history (`rebase -i`, `push --force`)
- Production app commands (capecraft) — always forbidden unless explicitly authorized

## 6) Branching and Commit Conventions
### 6.1 Branch naming
Use one of:
- `wo/<plan-id-lowercase>` (preferred)
- `wo/<area>-<short-desc>-###` (example: `wo/ui-footer-version-001`)

### 6.2 Single-commit default
- Default: **one commit per WO**
- Commit message format:
  - `fix(scope): ...`
  - `feat(scope): ...`
  - `docs(scope): ...`
  - `chore(scope): ...`

## 7) Work Order (WO) Format (required)
Every WO must contain:
- **Authority Chain header injection** (see §8)
- **Plan/WO ID**
- **Goal**
- **Scope (explicit files/dirs)**
- **Constraints / gates**
- **Acceptance criteria**
- **Verification commands** (copy/paste runnable)
- **Evidence pack** (required outputs)

## 8) Mandatory Header Injection (must prefix every WO instruction)
Every WO instruction must start with this exact header block:

Robert (final authority) → CapeAI (planning/governance) → VS_Chat (manager/orchestrator) → Codex (worker/implementer)  
**Sandbox-only:** autorisen (staging). **NO production (capecraft) deploy/release** unless Robert explicitly instructs it.  
Follow DEV_PLATFORM_SPEC.md. Execute end-to-end. Produce the evidence pack.

## 9) Evidence Pack (required output format)
The evidence pack must include, in this order:

1) **Preflight**
- `git status --porcelain`
- `git branch --show-current`
- `git --no-pager log -1 --oneline`

2) **Change summary**
- `git diff --stat`
- `git diff` (or a concise but complete summary if very large)

3) **Verification output**
- Paste command + output for each required verification command from the WO

4) **Artifacts**
- Any screenshots or notes for UI checks (desktop + mobile)
- Any URLs tested (staging)

5) **Commit proof**
- `git --no-pager show --name-only --oneline -1`
- `git status --porcelain` (must be clean)

## 10) Visual Verification Standard (UI work)
If the WO touches UI/layout:
- Confirm desktop + mobile using responsive viewport checks:
  - Mobile: 390×844 (or similar)
  - Tablet: 768×1024
  - Desktop: 1366×768 or higher
- Provide “what changed + where verified” in the evidence pack.

## 11) Deploy Policy (autorisen only, when explicitly requested)
If the WO includes staging deploy:
- Allowed:
  - `heroku container:push web -a autorisen`
  - `heroku container:release web -a autorisen`
  - Post-deploy checks: `curl -sS https://<autorisen-app>/api/version`, key endpoints
- Forbidden:
  - Any deploy/release to `capecraft` unless explicitly instructed by Robert

## 12) Definition of Done (DoD)
A WO is done when:
- Acceptance criteria are met
- Verification commands pass
- Evidence pack is complete and ordered
- Repo is clean after commit
- Scope boundaries respected
