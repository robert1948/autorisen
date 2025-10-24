# CITuneAgent Playbook

**Objective:** Ensure CI tooling is codified and consistent.

**Inputs:** `.pre-commit-config.yaml`, `.github/workflows/*.yml`

**Tasks:**
- Verify pre-commit hooks: markdownlint, black, ruff
- Normalize versions and minimal args
- Ensure CI runs pre-commit and pytest (smoke)

**Commands:**
1) `make codex-ci-validate`

**Done when:**
- PR with labels: `codex`, `ci-tune`, `needs-review`
- PR body lists hook versions used and skipped files (if any)
- Link to `docs/Agent_Scope_Boundaries.md`
