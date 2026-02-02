# RUNBOOK_VS_CHAT — Evidence-First Execution Loop

## Standard Loop (Always)
1) Preflight evidence
   - git status --porcelain
   - git branch --show-current
   - git log -1 --oneline

2) Identify scope
   - Confirm WO ID + acceptance criteria + autonomy level (L0–L3)
   - Confirm environment boundary (staging `autorisen` only)

3) Implement changes
   - Make smallest safe change
   - Prefer feature flags for behavior changes

4) Show diffs
   - git diff
   - git diff --stat

5) Stage intentionally
   - git add -p (preferred) or explicit paths

6) Verify
   - Run lint/test/typecheck (project-specific commands)
   - Re-run any targeted rg checks (routes, env, config)

7) Commit
   - Conventional commit style preferred
   - Include WO id in commit message footer or body

8) Evidence finalization
   - git diff --cached
   - git show --name-only --pretty=fuller

9) PR readiness
   - Summarize changes, risks, tests run, and evidence
   - No production deploy. Staging deploy only if WO explicitly permits (L3).

## Escalation Rules
- If stop condition triggers: halt and ask Robert with a short options list.
