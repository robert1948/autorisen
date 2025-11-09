# PlanSyncAgent Playbook

**Objective:** Keep `docs/autorisen_project_plan.csv` and `docs/Master_ProjectPlan.md` synchronized.

**Commands:**

1. `make codex-plan-diff`
1. If drift detected, `make codex-plan-apply`

**Allowed edits:**

- `docs/autorisen_project_plan.csv`
- `docs/Master_ProjectPlan.md` (within the fenced section `<!-- PLAN:BEGIN --> ... <!-- PLAN:END -->`)

**Done when:**

- PR created with labels: `codex`, `plan-sync`, `needs-review`
- PR body contains:
  - Machine-readable diff block (added/removed/changed IDs)
  - A regenerated table section in `Master_ProjectPlan.md`
  - Link to `docs/Agent_Scope_Boundaries.md`

**Notes:**

- CSV is treated as the source of truth for the table.
- MD may contain narrative above/below the fenced section; preserve it.
