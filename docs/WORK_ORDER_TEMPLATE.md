# WORK_ORDER_TEMPLATE.md
# CapeControl Work Order Template (WO)

Robert (final authority) → CapeAI (planning/governance) → VS_Chat (manager/orchestrator) → Codex (worker/implementer)  
**Sandbox-only:** autorisen (staging). **NO production (capecraft) deploy/release** unless Robert explicitly instructs it.  
Follow DEV_PLATFORM_SPEC.md. Execute end-to-end. Produce the evidence pack.

---

## WORK ORDER SUMMARY
- **PLAN / WO ID:** WO-____
- **Title:** ____
- **Goal:** ____
- **Owner:** VS_Chat → Codex executes
- **Target Environment:** autorisen-only (staging)

## 1) Scope
### In-scope files/dirs
- `...`
- `...`

### Out-of-scope (explicitly excluded)
- Production (`capecraft`)
- Migrations / schema changes (unless explicitly authorized below)
- Dependency upgrades (unless explicitly authorized below)
- Anything not listed in “In-scope files/dirs”

## 2) Constraints / Gates (must obey)
- **autorisen-only**
- **No production deploy/release**
- **No migrations** unless explicitly allowed here: (YES/NO) ___
- **No env var changes** unless explicitly allowed here: (YES/NO) ___
- **No dependency changes** unless explicitly allowed here: (YES/NO) ___
- **Single commit** unless specified otherwise: (YES/NO) ___

## 3) Acceptance Criteria (must be testable)
- [ ] Criterion 1 (observable)
- [ ] Criterion 2 (observable)
- [ ] Criterion 3 (observable)

## 4) Implementation Notes (optional, but helpful)
- UX rules, design tokens, routes, endpoints, etc.
- Any “must keep” behaviors
- Any known pitfalls

## 5) Verification Commands (required)
Paste exact commands to run and include output in evidence pack.

Example:
- `git status --porcelain`
- `npm -C client run build`
- `pytest -q`
- `curl -sS "$BASE/api/version"`

## 6) Visual Verification (if UI touched)
- [ ] Desktop viewport verified: ____ (include page/route)
- [ ] Mobile viewport verified: ____ (include page/route)
- [ ] Screenshot notes included in evidence pack

## 7) Evidence Pack (required, ordered)
Codex must return:

1) **Preflight**
- `git status --porcelain`
- `git branch --show-current`
- `git --no-pager log -1 --oneline`

2) **Change summary**
- `git diff --stat`
- `git diff`

3) **Verification output**
- Command + output for each verification command above

4) **Artifacts**
- UI checks: viewports + where verified
- Any staging URLs checked

5) **Commit proof**
- `git --no-pager show --name-only --oneline -1`
- `git status --porcelain` (clean)

## 8) Deploy to Staging (only if explicitly required)
If deploy is required, include one of:

### Option A: Container deploy (autorisen)
- `heroku container:push web -a autorisen`
- `heroku container:release web -a autorisen`
- Post-deploy:
  - `curl -sS https://<autorisen-app>/api/version`
  - `curl -sS -o /dev/null -w "%{http_code}\n" https://<autorisen-app>/api/auth/me`

### Option B: No deploy required
State: “No deploy in this WO.”

## 9) Stop Conditions (when Codex must stop and ask)
- Any conflict with DEV_PLATFORM_SPEC guardrails
- Any need to expand scope beyond §1
- Any failed verification that cannot be fixed without expanding scope
