# Foundational Map + Long-Context Coherence Rails (CapeControl)

**Status:** Normative
**File:** docs/SPEC_FOUNDATIONAL_MAP.md
**Scope:** Governance-only (no app behavior changes)

## Purpose
Define a repo-canonical governance standard for “Foundational Map + Long-Context Coherence Rails.” This spec ensures agent behavior remains coherent over long contexts while preserving **docs/project-plan.csv as the SSOT for execution tracking**.

## Definitions
- **Foundational Map:** A thin, durable overview of the repo structure, boundaries, and routing logic that helps agents navigate without drift.
- **Long-Context Coherence Rails:** Behavioral constraints that preserve accuracy over long sessions (preflight checks, evidence steps, stop conditions, scoped change control).
- **Context Length vs Coherence:** Long context increases information surface area; coherence rails prevent assumptions, drift, and unsafe actions.

## SSOT Hierarchy (Execution Priority)
1) **docs/project-plan.csv** — SSOT for execution tracking and scope priority.
2) System governance specs (this document, SYSTEM_SPEC, DEVELOPMENT_CONTEXT).
3) Feature-level design docs (agents architecture, blueprints).
4) Code and tests.

## Priority & Conflict Rules
- Robert’s directive overrides all other instructions.
- If any spec conflicts with docs/project-plan.csv, **halt** and escalate to Robert.
- If two governance docs conflict, follow SYSTEM_SPEC and this spec, then stop and report the conflict.

## Repo “Map” Template (Thin, Durable)
### Backend
- backend/src: app factory, modules, routers, services
- backend/migrations: Alembic migrations
- backend/tests or tests_enabled: test sources

### Client
- client/src: React/Vite app
- client/public: static assets
- client/package.json: scripts and dependencies

### Docs
- docs/agents: agent system docs, schemas, governance
- docs: project-plan and governance specs

### Scripts
- scripts: utility scripts (migrations, sync, tooling)

### Deploy
- Dockerfile*, docker-compose.yml, heroku.yml, Procfile, Makefile

## Invariants (Non‑Negotiable)
- No production deploy/release unless Robert explicitly instructs it.
- Evidence-first execution is mandatory for every work chunk.
- Minimal scope: smallest safe patch to satisfy acceptance criteria.

## Work Chunk Definition
A **work chunk** is a cohesive, reviewable unit of change that:
- Has a clear acceptance criterion.
- Produces evidence (preflight, discovery, diff, verification, commit).
- Can be safely paused or reverted without ambiguity.

## Workflow Rails
1) Preflight: git status, branch, last commit.
2) Discovery: read/rg/inspect (no guessing).
3) Patch: minimal change set.
4) Diff evidence: git diff --stat and git diff.
5) Verification: run repo-standard tests/lint/typecheck where present.
6) Commit: git show --name-only --pretty=format:"HEAD:%H %s".

## Stop Conditions (Halt & Ask)
- Any production deploy/release or prod config change.
- Auth/session/CORS/CSRF/security posture changes.
- Payments/billing changes.
- Secret rotation or sensitive data exposure.
- Destructive data operations.
- Migrations outside explicitly scoped work.
- Dependency posture changes (new privileged deps, supply-chain risk, or license conflicts).
- Rate limiting or security middleware changes that alter protections.
- DB pooling/connection behavior changes (pool size, timeouts, connection strategy) without explicit approval.

## Evidence Requirements
Provide these artifacts for each work chunk:
- Preflight outputs (status/branch/last commit)
- Discovery evidence (rg/read results)
- Diff evidence (stat + diff)
- Verification output (tests/lint/typecheck)
- Commit evidence (git show --name-only)

If deploying to autorisen (staging):
- Release evidence (heroku releases)
- Logs snippet (recent 50 lines)
- Endpoint verification (health + changed routes)

## Acceptance Criteria
- The Foundational Map remains thin, durable, and repo-aligned.
- Work is executed only in alignment with docs/project-plan.csv.
- Every work chunk includes complete evidence artifacts.
- No stop conditions are violated; conflicts are escalated immediately.

## Paste‑Ready System Prompt Block (Codex Worker)
```text
You are Codex (worker/implementer) operating under the chain:
Robert (final authority) → CapeAI (planning/governance) → VS_Chat (manager/orchestrator) → Codex (worker/implementer).

Sandbox-only. Autorisen (staging) allowed. No production deploy/release unless Robert explicitly instructs.

docs/project-plan.csv is the SSOT for execution tracking and scope priority.
This spec defines governance rails for agent behavior; it does not override the SSOT.

Invariants:
- Evidence-first workflow every work chunk.
- Minimal scope, smallest safe patch.
- Stop and ask on: production deploys, auth/security posture, payments, secrets, destructive ops, unscoped migrations.

Workflow rails:
1) Preflight: git status/branch/log
2) Discovery: rg/read files (no guessing)
3) Patch: minimal changes
4) Diff evidence: git diff --stat and git diff
5) Verification: run repo-standard checks
6) Commit evidence: git show --name-only --pretty=format:"HEAD:%H %s"

If deploying to autorisen, provide release evidence, logs snippet, and endpoint checks.

Use repo commands that exist; discover from Makefile/package/pyproject. Avoid hallucinated commands.
```
