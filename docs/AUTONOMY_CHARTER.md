# AUTONOMY_CHARTER — VS_Chat Operating Authority (Staging-Only)

## Authority Chain
Robert (final authority) → CapeAI (planning/governance) → VS_Chat (manager/orchestrator) → Codex (worker/implementer)

## Environment Boundary
- Allowed: local dev + Heroku staging `autorisen`
- Forbidden: production `capecraft` deploy/release unless Robert explicitly instructs it

## Autonomy Levels
- L0 Suggest only (no code changes)
- L1 Changes + show diff (no commit)
- L2 Changes + tests + commit to branch
- L3 Changes + tests + PR + staging deploy to `autorisen` (only when WO explicitly allows)

## Allowed Scope (Default)
- Docs/spec updates
- UI polish / accessibility
- Refactors that preserve behavior
- Test additions
- Small bug fixes with tests

## Approval Required (Stop & Ask)
- Any production deploy/release
- DB migrations / schema changes
- Auth/session/CORS/CSRF/security posture
- Payments/billing
- Secret rotation / credential changes
- Data deletion, destructive scripts, or anything with loss risk

## Stop Conditions (Must Halt)
- Failing tests with unclear fix
- Ambiguous requirements or missing acceptance criteria
- Touching any “Approval Required” area
- Unexpected routes/endpoints/config changes
- Any sign of secrets exposure risk

## Definition of Done (Evidence-First)
Every autonomous task must include:
- Preflight: git status/branch/log
- Diff: before/after (working tree + staged)
- Tests: lint/test/typecheck as applicable
- Final: `git show --name-only` on commit
- WO record: ID + acceptance criteria + evidence commands

## Repo Settings (Documented Requirements)
These settings are required in GitHub but cannot be enforced by code alone:
- Branch protection: PR required, no direct pushes to default branch
- Required checks: lint/test/typecheck for PR merge
- Review required for high-risk labels (auth/security/payments/migrations)
