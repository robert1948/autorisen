# WO-LANDING-PROGRESSIVE-REG-002 — Landing Progressive Registration (v2)

**Status:** draft (restored artifact)
**Priority:** P0
**Environment:** autorisen (staging/sandbox) only
**Production boundary:** NO capecraft/prod deploys or releases unless Robert explicitly instructs.

## 1) Purpose
Implement or refine “progressive registration” on the public landing experience so users can start with minimal friction and only provide additional details when value/trust is established.

## 2) Scope (MVP-safe)
- Landing flow updates related to progressive registration only.
- Minimal, reversible changes.
- No new product scope beyond what is already defined in SYSTEM_SPEC and current MVP.

## 3) Non-goals / Hard constraints
- No production (capecraft) changes.
- No secrets handling in repo.
- No destructive operations.
- No running migrations unless explicitly authorized by Robert.
- No major redesign outside the landing + registration/onboarding path.

## 4) Inputs / References
- SYSTEM_SPEC: docs/SYSTEM_SPEC.md (onboarding/registration gates & UX rules)
- Routes/Pages doc (if relevant): docs/MVP_PAGES_AND_ROUTES.md
- SSOT row: docs/project-plan.csv → WO-LANDING-PROGRESSIVE-REG-002

## 5) Execution Plan (follow in order)
1. Preflight evidence (git status/branch/log).
2. Identify current landing + auth/onboarding components involved.
3. Implement progressive registration step(s) with minimal UI + state changes.
4. Ensure routing remains consistent with MVP routes.
5. Add/adjust any documentation required by SSOT.
6. Verification (see below).
7. Commit(s) with WO id in message.
8. Push branch.

## 6) Verification Commands (minimum)
Run what applies based on changes:
- `npm test` (if configured)
- `npm run build` (frontend)
- `rg` route checks for landing/register paths
- `git diff --stat && git diff` before commit

## 7) Definition of Done
- Progressive registration behavior matches the intended gates (minimal first step, later details).
- No route regressions.
- Build/tests (as applicable) pass.
- SSOT updated/closed with reference commit (if required by process).
- Branch pushed.

