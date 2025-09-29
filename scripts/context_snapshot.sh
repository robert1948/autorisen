#!/usr/bin/env sh
# Generate context/latest.txt summarising repo state for Codex tasks.
set -eu

if ! command -v git >/dev/null 2>&1; then
  echo "git command not found" >&2
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel)"
cd "${ROOT}"

OUT_DIR="${ROOT}/context"
OUT_FILE="${OUT_DIR}/latest.txt"

mkdir -p "${OUT_DIR}"

TMP="$(mktemp)"
trap 'rm -f "${TMP}"' EXIT

REPO_META="GitHub CLI unavailable"
if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    REPO_META="$(gh repo view --json nameWithOwner,isPrivate,defaultBranchRef \
      --jq '.nameWithOwner + " (private: " + ( .isPrivate | tostring) + ", default: " + .defaultBranchRef.name + ")"')"
  else
    REPO_META="gh auth missing (run 'gh auth login')"
  fi
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
LATEST_COMMIT="$(git log -1 --pretty=format:'%h %an %ad %s' --date=short)"

STATUS="$(git status --short || true)"
if [ -z "${STATUS}" ]; then
  STATUS="clean"
else
  STATUS="$(printf '%s\n' "${STATUS}" | head -n 40)"
fi

KEY_FILES="$(git ls-tree -r --name-only HEAD \
  | grep -E '^(backend/src/app|backend/src/modules|client/src|frontend/src|docs|scripts)/' || true)"
if [ -n "${KEY_FILES}" ]; then
  KEY_FILES="$(printf '%s\n' "${KEY_FILES}" | head -n 80)"
fi

TEST_FILES="$(git ls-tree -r --name-only HEAD \
  | grep -E '^(backend/tests|tests)/' || true)"
if [ -n "${TEST_FILES}" ]; then
  TEST_FILES="$(printf '%s\n' "${TEST_FILES}" | head -n 40)"
fi

README_SNIPPET=""
if [ -f "README.md" ]; then
  README_SNIPPET="$(sed -n '1,40p' README.md)"
fi

ISSUES="gh issue list unavailable"
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
ISSUES_RESULT="$(gh issue list --state open --label ready --limit 10 \
    --json number,title,assignees \
    --jq '.[] | "#" + (.number|tostring) + " " + .title + (if (.assignees|length)>0 then " (assignees: " + ( [.assignees[].login] | join(", ") ) + ")" else "" end)')"
  if [ -n "${ISSUES_RESULT}" ]; then
    ISSUES="${ISSUES_RESULT}"
  else
    ISSUES="none"
  fi
fi

{
  printf '# Repository Snapshot\n'
  printf '\n## Repository\n'
  printf 'GitHub: %s\n' "${REPO_META}"
  printf 'Branch: %s\n' "${BRANCH}"
  printf 'Latest Commit: %s\n' "${LATEST_COMMIT}"

  printf '\n## Working Tree\n'
  printf '%s\n' "${STATUS}" | sed 's/^/- /'

  printf '\n## Key Files (tracked)\n'
  if [ -n "${KEY_FILES}" ]; then
    printf '%s\n' "${KEY_FILES}" | sed 's/^/- /'
  else
    printf '- (none matched)\n'
  fi

  printf '\n## Test Suites\n'
  if [ -n "${TEST_FILES}" ]; then
    printf '%s\n' "${TEST_FILES}" | sed 's/^/- /'
  else
    printf '- (no tests captured)\n'
  fi

  printf '\n## Ready Issues\n'
  printf '%s\n' "${ISSUES}" | sed 's/^/- /'

  if [ -n "${README_SNIPPET}" ]; then
    printf '\n## README.md (first 40 lines)\n'
    printf '%s\n' "${README_SNIPPET}" | sed 's/^/  /'
  fi
} >"${TMP}"

mv "${TMP}" "${OUT_FILE}"
echo "Wrote ${OUT_FILE}"
