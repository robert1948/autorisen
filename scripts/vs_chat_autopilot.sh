#!/usr/bin/env bash
set -euo pipefail

REPO="/home/robert/Development/capecontrol"
BASE_BRANCH="wo/db-003"   # autopilot SSOT authority branch
cd "$REPO"

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

print_ssot_row() {
  local id="$1"
  python3 - <<PY
import csv
ID="$id"
p="docs/project-plan.csv"
with open(p, newline="", encoding="utf-8") as f:
    rows=list(csv.DictReader(f))
row=[r for r in rows if r.get("id")==ID]
if not row:
    raise SystemExit(f"STOP: SSOT row not found for {ID}")
row=row[0]
for k in ("id","task","owner","status","priority","notes","artifacts","verification_commands"):
    print(f"{k}: {row.get(k)}")
PY
}

is_gated_item() {
  local id="$1"
  python3 - <<PY
import csv
ID="$id"
p="docs/project-plan.csv"
with open(p, newline="", encoding="utf-8") as f:
    rows=list(csv.DictReader(f))
row=[r for r in rows if r.get("id")==ID][0]
blob=" ".join([row.get("task",""), row.get("notes",""), row.get("artifacts","")]).lower()

# Gate keywords (auto-block)
keywords = [
  "backend", "security", "payments", "stripe", "payfast", "auth",
  "jwt", "csrf", "cookie", "secrets", "token", "key",
  "migration", "alembic", "database schema", "ddl"
]

if any(k in blob for k in keywords):
    print("GATED")
else:
    print("OK")
PY
}

block_ssot() {
  local id="$1"
  local reason="$2"

  python3 - <<PY
import csv
from pathlib import Path
ID="$id"
REASON="$reason"
p=Path("docs/project-plan.csv")
rows=[]
with p.open(newline="", encoding="utf-8") as f:
    r=csv.DictReader(f)
    fieldnames=r.fieldnames
    for row in r:
        if row.get("id")==ID:
            row["status"]="blocked"
            notes=(row.get("notes") or "").strip()
            tag=f"blocked: {REASON}"
            row["notes"]= (notes + ("; " if notes else "") + tag) if tag.lower() not in notes.lower() else notes
        rows.append(row)

if not any(r.get("id")==ID for r in rows):
    raise SystemExit(f"SSOT row not found: {ID}")

out=[]
out.append(",".join(fieldnames))
for row in rows:
    out.append(",".join((row.get(k,"") or "").replace("\n"," ").replace("\r"," ") for k in fieldnames))
p.write_text("\n".join(out) + "\n", encoding="utf-8")
PY

  safe_run "git add docs/project-plan.csv"
  safe_run "git diff --cached --name-only"
  safe_run "git commit -m \"chore(ssot): auto-block $id ($reason)\""
  safe_run "git push -u origin $(git branch --show-current)"
}

checkout_base() {
  safe_run "git checkout $BASE_BRANCH"
  safe_run "git pull --rebase"
}

checkout_wo_branch_from_base() {
  local id="$1"
  local br="wo/${id,,}"

  # If exists, resume. If not, create from BASE_BRANCH.
  if git show-ref --verify --quiet "refs/heads/$br"; then
    safe_run "git checkout $br"
    return
  fi
  if git ls-remote --exit-code --heads origin "$br" >/dev/null 2>&1; then
    safe_run "git fetch origin $br:$br"
    safe_run "git checkout $br"
    return
  fi
  safe_run "git checkout -b $br $BASE_BRANCH"
}

while true; do
  echo "=== BASE PREFLIGHT ==="
  checkout_base
  safe_run "git status --porcelain"
  safe_run "git branch --show-current"
  safe_run "git --no-pager log -1 --oneline"

  id="$(pick_next_id)"
  if [[ "$id" == "NO_ELIGIBLE_WORK" ]]; then
    echo "PIPELINE_EMPTY"
    echo "SLEEPING 60s (idle)"
    sleep 60
    continue
  fi

  echo "=== NEXT: $id ==="
  print_ssot_row "$id"

  gate="$(is_gated_item "$id")"
  if [[ "$gate" == "GATED" ]]; then
    echo "AUTO-BLOCK (gated): $id"
    block_ssot "$id" "gated item (backend/auth/payments/security/migrations/secrets)"
    continue
  fi

  runbook="scripts/runbooks/$id.sh"
  if [[ ! -f "$runbook" ]]; then
    echo "AUTO-BLOCK (missing runbook): $id"
    block_ssot "$id" "missing runbook: $runbook"
    continue
  fi

  echo "=== WO BRANCH ==="
  checkout_wo_branch_from_base "$id"
  safe_run "git branch --show-current"
  safe_run "git --no-pager log -1 --oneline"

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

  # === MERGE WO -> BASE (advance SSOT + history) ===
  wo_branch="$(git branch --show-current)"
  echo "=== MERGE BACK INTO BASE: $wo_branch -> $BASE_BRANCH ==="
  checkout_base
  safe_run "git merge --ff-only $wo_branch" || { echo "STOP: cannot ff-merge $wo_branch into $BASE_BRANCH"; exit 94; }
  safe_run "git push -u origin $BASE_BRANCH"
done
