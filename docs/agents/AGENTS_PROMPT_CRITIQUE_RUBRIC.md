# AGENTS.md Critique Rubric (CapeControl)

## How to Use
When iterating on `AGENTS.md` (or any agent “map” doc), evaluate against this rubric.
Score each category 0–2:
- 0 = missing / unsafe
- 1 = present but weak
- 2 = clear, enforceable, repo-aligned

Total score target: **≥ 16/20** before adopting changes.

---

## 1) Repo Orientation (0–2)
- Does it correctly describe what CapeControl is (evidence-first orchestration)?
- Does it point to the SSOT docs (SYSTEM_SPEC, DEVELOPMENT_CONTEXT, project-plan)?

## 2) Boundaries & Stop Conditions (0–2)
- Explicitly forbids production deploy/release unless Robert instructs.
- Defines “STOP + ASK” zones (auth/security, payments, migrations, secrets, destructive ops).

## 3) Evidence-First Execution Loop (0–2)
- Requires preflight (git status/branch/log).
- Requires discovery (rg/file inspection; no guessing).
- Requires diff evidence (stat + diff).
- Requires verification (tests/lint/typecheck where present).
- Requires commit evidence (git show --name-only).

## 4) Context Efficiency (0–2)
- Thin map: short, structured, scannable.
- Depth moved into linked docs rather than huge prompt blocks.

## 5) Command Truthfulness (0–2)
- Uses only commands that exist in the repo (no invented Make targets).
- Points the agent to discover commands from package/pyproject/Makefile.

## 6) Security & Least Privilege (0–2)
- Avoids encouraging secret exposure.
- Staging-only credentials; no prod tokens in agent context.
- Safe handling of logs/output (redact secrets).

## 7) Change Control (0–2)
- Encourages branch-first workflow; PR if standard.
- Mentions required checks/CI where relevant.
- Requires WO/acceptance criteria for non-trivial work.

## 8) Drift Resistance (0–2)
- Prevents “platform rewrite” behavior.
- Prefers smallest safe patch; incremental work chunks.

## 9) External Critique Safety (0–2)
- Provides guidance to sanitize/redact before sharing with external models/tools.
- Suggests using an `AGENTS.public.md` if needed.

## 10) Verification Hooks (0–2)
- Requires staging verification on `autorisen` when deploying.
- Requires rollback note or revert path.

---

## Reviewer Output Template
- Rubric scores (1–10): …
- Top 3 risks: …
- Top 3 improvements: …
- Any violations of stop conditions: (yes/no; details)
