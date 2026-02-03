# CapeControl — Codex Agent Instructions (Repo Root)

## Authority & Safety
Authority Chain: Robert (final authority) → CapeAI (planning/governance) → VS_Chat (manager/orchestrator) → Codex (worker/implementer)

Safety Gate: autorisen-only (staging/sandbox). NO capecraft production deploy/release unless Robert explicitly instructs it.

## Operating Mode (Default)
1) Plan first (Chat mode). No edits until the plan is approved.
2) Execute (Agent mode) only after approval.
3) Use Git checkpoints: branch → diff → verify → commit → push.

## Hard Stops (Must ask before proceeding)
- Any production deploy/release (capecraft)
- DB migrations/schema changes
- Auth/CSRF/security policy changes
- Payments (PayFast/Stripe) behavior changes
- Infra/pipeline changes (Heroku, AWS, CI/CD)

## Where the detailed playbooks live
- docs/agents/codex/ : role/agent guidance and operating playbooks
- docs/agents/codex-tasks/ : task briefs (work orders) for Codex execution

## Minimum Evidence After Any Change
- show: `git diff`
- run: the relevant verification commands
- summarize: what changed + why
