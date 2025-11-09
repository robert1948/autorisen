# TestGuardianAgent Playbook

**Objective:** Keep auth/CSRF regression tests green with safe, reviewable changes.

**Scope:** Test fixtures only. Do **not** change app logic.

**Commands:**

1. `make codex-test-dry`
1. If specific fixture regeneration is appropriate:
   - `make codex-test-heal`

**Allowed edits:** `tests/**`, `scripts/regenerate_fixtures.py`, fixture files

**Done when:**

- PR opened with labels: `codex`, `test-guardian`, `needs-review`
- PR lists failing tests observed, steps executed, and resulting status
- Link to `docs/Agent_Scope_Boundaries.md`
