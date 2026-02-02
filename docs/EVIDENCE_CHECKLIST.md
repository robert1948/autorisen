# EVIDENCE_CHECKLIST — Required Outputs Per Work Order

## Preflight (paste outputs)
- git status --porcelain
- git branch --show-current
- git log -1 --oneline

## Implementation Evidence
- git diff --stat
- git diff

## Verification Evidence (paste outputs)
- lint command + output
- tests command + output
- typecheck command + output (if applicable)

## Staging (only if explicitly allowed)
- Deploy command + logs (autorisen only)

## Final Evidence
- git diff --cached
- git show --name-only --pretty=format:"HEAD:%H %s"
