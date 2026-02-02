#!/usr/bin/env bash
set -euo pipefail
cd /home/robert/Development/capecontrol
source scripts/guardrails.sh

pick_next_id() {
  python3 - <<'PY'
import csv, re
p="docs/project-plan.csv"
def norm(x): return (x or "").strip().lower()
prio_rank={"p0":0,"p1":1,"p2":2,"p3":3}
with open(p, newline="", encoding="utf-8") as f:
    rows=list(csv.DictReader(f))

def is_blocked(r):
    blob=" ".join([r.get("status",""), r.get("notes","")])
    return bool(re.search(r"\bblocked\b", blob, flags=re.I))

active=[r for r in rows if norm(r.get("status")) not in ("done","closed")]
active_sorted=sorted(active, key=lambda r:(prio_rank.get(norm(r.get("priority")),9), r.get("id","")))

def pick(priority, status):
    for r in active_sorted:
        if norm(r.get("priority"))==priority and norm(r.get("status"))==status and not is_blocked(r):
            return r
    return None

next_item = (
    pick("p0","in_progress") or pick("p0","in progress")
    or pick("p0","planned")
    or pick("p1","planned")
)

print("NO_ELIGIBLE_WORK" if not next_item else next_item["id"])
PY
}

checkout_branch() {
  local id="$1"
  local br="wo/${id,,}"
  if git show-ref --verify --quiet "refs/heads/$br"; then
    safe_run "git checkout $br"; return
  fi
  if git ls-remote --exit-code --heads origin "$br" >/dev/null 2>&1; then
    safe_run "git fetch origin $br:$br"
    safe_run "git checkout $br"; return
  fi
  safe_run "git checkout -b $br"
}

print_ssot_row() {
  local id="$1"
  python3 - <<PY
import csv
ID="$id"
p="docs/project-plan.csv"
with open(p, newline="", encoding="utf-8") as f:
    rows=list(csv.DictReader(f))
row=[r for r in rows if r.get("id")==ID]
if not row: raise SystemExit(f"STOP: SSOT row not found for {ID}")
row=row[0]
for k in ("id","task","owner","status","priority","notes","artifacts","verification_commands"):
    print(f"{k}: {row.get(k)}")
PY
}

while true; do
  echo "=== PREFLIGHT ==="
  safe_run "git status --porcelain"
  safe_run "git branch --show-current"
  safe_run "git --no-pager log -1 --oneline"

  id="$(pick_next_id)"
  if [[ "$id" == "NO_ELIGIBLE_WORK" ]]; then
    echo "PIPELINE_EMPTY"; exit 0
  fi

  echo "=== NEXT: $id ==="
  checkout_branch "$id"
  safe_run "git branch --show-current"
  safe_run "git --no-pager log -1 --oneline"
  print_ssot_row "$id"

  runbook="scripts/runbooks/$id.sh"
  if [[ ! -f "$runbook" ]]; then
    echo "STOP: missing runbook: $runbook" >&2
    exit 92
  fi

  log="logs/${id}_$(date +%Y%m%d_%H%M%S).log"
  echo "=== RUN: $runbook (log: $log) ==="
  bash "$runbook" |& tee "$log"

  echo "=== POST: repo-truth ==="
  safe_run "git status --porcelain"
  safe_run "git diff --stat"

  if [[ -n "$(git status --porcelain)" ]]; then
    echo "STOP: runbook left uncommitted changes (must commit/push inside runbook)." >&2
    exit 93
  fi
done
