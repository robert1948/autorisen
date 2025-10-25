# Codex PR Template

<!-- Optimized for agent-run changes. Keep sections concise and machine-readable. -->

## 📌 Summary

- **Playbook:** <!-- e.g., doc-clean | plan-sync | ci-tune | test-guardian -->
- **Scope labels:** <!-- ensure includes `codex` + specific playbook label -->
- **Branch:** <!-- expected: codex/<playbook>/<date>-<shortid> -->

## 🧪 Commands Executed (in order)

<!-- Paste exact commands Codex ran, one per line, no prose -->
## 📁 Changes

- **Files changed (count):** <!-- number -->
- **Generated/Updated paths:** <!-- short list or globs -->
- **Skipped paths (if any):** <!-- list -->

## 🔍 Results & Output

- **Pre-commit status:** <!-- pass | warnings (count) -->
- **Pytest status (smoke):** <!-- pass | warnings | N fails -->
- **Notable warnings:** <!-- bullets or 'None' -->

## 🧭 Plan Sync Drift (if applicable)

<!-- Machine-readable diff block from scripts/plan_sync.py --check-only -->
```diff
# + ID AUTH-010
# - ID FE-001

sample
