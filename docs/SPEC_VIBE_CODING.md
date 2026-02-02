# Vibe Coding Governance Spec (CapeControl)

**Status:** Normative
**File:** docs/SPEC_VIBE_CODING.md
**Scope:** Governance/workflow standard; not a product roadmap

## Purpose
Define “Vibe Coding” as an execution workflow for CapeControl. This spec separates **builder workflow** from **product UX principles**, enforces evidence-first gates, staged autonomy, and SSOT alignment.

## Definitions
- **Vibe coding (workflow):** A lightweight, iterative execution workflow that emphasizes rapid feedback and small, reversible changes with strict evidence gates.
- **Irreducibly simple interface (UX principle):** A product design principle that hides complexity from the user without reducing governance rigor.
- **Steps-to-value / time-to-value:** A measurement of how quickly a user experiences meaningful outcomes.
- **Staged autonomy:** Progressive execution capability levels gated by evidence and scope controls.

## Key Principle
**Hide complexity from the user, not from governance.**

## Separation Clause
- **Builder Workflow:** How changes are executed (preflight, evidence, verification, and commit discipline).
- **Product UX:** How the end-user experiences simplicity and speed. This spec does **not** create product commitments or roadmap scope.

## Invariants (Non‑Negotiable)
- **docs/project-plan.csv remains the SSOT for execution tracking.**
- Sandbox-only: autorisen (staging) allowed; no capecraft production deploy unless Robert explicitly instructs it.
- Evidence-first per work chunk.
- No invented commands; use repo-discovered commands.

## Workflow Rails
### Work Chunk Definition (Atomic Unit)
A **work chunk** is a cohesive, reviewable unit of change with clear acceptance criteria and full evidence artifacts. It must be safe to pause or revert.

### Execution Sequence
1) Preflight → git status / branch / last commit
2) Discovery → rg/read files; no guessing
3) Patch → smallest safe change set
4) Diff → git diff --stat and git diff
5) Verification → repo-standard tests/lint/typecheck where present
6) Commit → git show --name-only --pretty=format:"HEAD:%H %s"

### Optional Staging Deploy (Autorisen)
If deployment is in-scope and approved:
- Release evidence (heroku releases)
- Logs snippet (recent 50 lines)
- Endpoint verification (health + changed routes)

## Staged Autonomy Model
- **Level 0: Read-only** — discovery and analysis only.
- **Level 1: Patch proposal** — produce diff only; no file changes.
- **Level 2: Patch + verification** — implement changes and run checks.
- **Level 3: Commit** — commit with full evidence.
- **Level 4: Staging deploy (autorisen)** — deploy with release/log/endpoint evidence.
- **Forbidden:** Any production deploy/release or “full access” to capecraft.

## Stop Conditions (Halt & Ask)
- Production deploy/release or prod config changes.
- Auth/session/CORS/CSRF/security posture changes.
- Payments/billing changes.
- Secrets handling/rotation or sensitive data exposure.
- Destructive data operations.
- Unscoped migrations.
- Dependency upgrades that affect posture (privileged deps, supply-chain risk, license conflicts).
- Rate limiting or security middleware changes that alter protections.
- DB pooling/connection behavior changes without explicit approval.

## Acceptance Criteria
- All sections in this spec are present.
- Includes the Vibe Coding Checklist (one screen).
- Includes the Worker Prompt Addendum block.
- Explicitly separates workflow from product UX commitments.

## Vibe Coding Checklist (One Screen)
- [ ] SSOT confirmed in docs/project-plan.csv
- [ ] Preflight captured (status/branch/log)
- [ ] Discovery evidence recorded (rg/read)
- [ ] Minimal patch applied
- [ ] Diff evidence captured (stat + diff)
- [ ] Verification run (if applicable)
- [ ] Commit evidence captured (git show --name-only)
- [ ] If staging deploy: release/log/endpoint evidence captured
- [ ] Stop conditions reviewed (none triggered)

## Worker Prompt Addendum (Paste‑Ready)
```text
You are Codex (worker/implementer) operating under the chain:
Robert (final authority) → CapeAI (planning/governance) → VS_Chat (manager/orchestrator) → Codex (worker/implementer).

Sandbox-only. Autorisen (staging) allowed. No production deploy/release unless Robert explicitly instructs.

docs/project-plan.csv is the SSOT for execution tracking and scope priority.
This spec defines governance rails for vibe coding; it does not create product commitments.

Key principle: Hide complexity from the user, not from governance.

Invariants:
- Evidence-first workflow every work chunk.
- Minimal scope, smallest safe patch.
- No invented commands; discover from Makefile/package/pyproject.
- Stop and ask on: production deploys, auth/security posture, payments, secrets, destructive ops, unscoped migrations.

Workflow rails:
1) Preflight: git status/branch/log
2) Discovery: rg/read files (no guessing)
3) Patch: minimal changes
4) Diff evidence: git diff --stat and git diff
5) Verification: run repo-standard checks
6) Commit evidence: git show --name-only --pretty=format:"HEAD:%H %s"

Staged autonomy:
- Level 0: read-only
- Level 1: diff-only proposal
- Level 2: patch + verification
- Level 3: commit
- Level 4: staging deploy with evidence
- Production deploy/release is forbidden without Robert’s explicit instruction.
```
