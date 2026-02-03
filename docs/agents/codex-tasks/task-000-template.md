# task-000-template — Codex Work Brief

## Goal
(One sentence. What outcome do we want?)

## Scope
- In scope:
- Out of scope:

## Safety Gate
- autorisen-only (staging/sandbox)
- NO capecraft production deploy/release unless Robert explicitly instructs it

## Hard Stops (ask before proceeding)
- DB migrations/schema changes
- Auth/CSRF/security policy changes
- Payments behavior changes (PayFast/Stripe)
- Infra/CI/CD/pipeline changes
- Anything not explicitly in scope

## Preflight Evidence (paste outputs)
```bash
cd /home/robert/Development/capecontrol
git status --porcelain
git branch --show-current
git --no-pager log -1 --oneline
```

## Plan (Chat mode only)

1.
2.
3.

## Execution Steps (Agent mode after approval)

1.
2.
3.

## Verification Commands

(Choose the smallest correct set. Examples:)

### Docs-only

```bash
# spell/markdown checks if available
rg -n "TODO|FIXME" docs || true
```

### Frontend (if relevant)

```bash
cd client
npm test
npm run build
```

### Backend (if relevant)

```bash
pytest -q
```

## Evidence to Attach

* `git --no-pager diff --stat`
* `git --no-pager diff`
* Verification command outputs

## Commit Message

(Use conventional commit style)
Example:
`docs(codex): <short description> (TASK-###)`
