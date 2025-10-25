# Dev Log — Autolocal / CapeControl

## 2025-10-25

**Focus:** Playbooks tracking, Makefile hygiene, and automation prep.

### What happened

- Fixed duplicate Makefile targets and warnings for `playbook-overview`, `playbook-open`, `playbook-badge`.
- Added/validated generator **scripts/gen_playbooks_overview.py** (creates `docs/PLAYBOOKS_OVERVIEW.md` with a status summary).
- Ran `make playbook-overview` — tracker updated cleanly.
- Prepared CI workflow to auto-regenerate tracker and update README badge when progress changes.
- Standardized Heroku pipeline targets and kept quick smoke targets.
- Added Docker Hub maintenance targets (description/README update via API).

### Useful commands

```bash
make playbook-overview
make playbook-badge
make heroku-login heroku-apps heroku-pipeline
make deploy-staging && make heroku-smoke-staging
