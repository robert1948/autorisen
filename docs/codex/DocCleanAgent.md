# DocCleanAgent Playbook

**Objective:** Standardize Markdown documents to repo style.

**Inputs:** `.pre-commit-config.yaml`, any `.markdownlint*`, `docs/**/*.md`, `README.md`

**Commands (in order):**

1. `make codex-docs-fix`
1. `make codex-docs-lint`

**Allowed edits:** `**/*.md` only.

**Done when:**

- Lint returns exit 0
- PR opened with labels: `codex`, `doc-clean`, `needs-review`
- PR body includes:
  - Summary of commands executed
  - Count of files changed
  - Before/after snippet for 3 representative docs
  - Link to `docs/Agent_Scope_Boundaries.md`
