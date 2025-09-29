#!/usr/bin/env python3
"""Generate a concise Markdown snapshot from docs/autorisen_project_plan.csv
Writes output to docs/Master_ProjectPlan.generated.md (non-destructive).
"""
import csv
from collections import Counter
from datetime import date

CSV = "docs/autorisen_project_plan.csv"
OUT = "docs/Master_ProjectPlan.generated.md"


def norm_row(row):
    # Normalize keys to lowercase without spaces/underscores for tolerant lookup
    normalized = {}
    for k, v in row.items():
        if k is None:
            continue
        key = k.strip().lower().replace(" ", "").replace("_", "")
        normalized[key] = (v or "").strip()
    return normalized


def pick(r, candidates, default=""):
    for c in candidates:
        v = r.get(c, "")
        if v:
            return v
    return default


with open(CSV, newline="") as f:
    reader = csv.DictReader(f)
    raw_rows = list(reader)

rows = [norm_row(r) for r in raw_rows]

# Determine keys
status_counts = Counter(r.get("status", "unknown") for r in rows)
total = len(rows)


# Priority detection: accept P1 or High as top priority
def is_p1(r):
    p = r.get("priority", "").upper()
    return p in ("P1", "HIGH", "P1-") or p.startswith("P1")


p1_tasks = rows if not rows else [r for r in rows if is_p1(r)][:12]

today = date.today().isoformat()

with open(OUT, "w") as o:
    o.write("# Master Project Plan (generated snapshot) — autorisen\n\n")
    o.write("Snapshot: " + today + "\n\n")
    o.write("- Total tasks: " + str(total) + "\n")
    o.write("- Status counts: " + ", ".join(f"{k}: {v}" for k, v in status_counts.items()) + "\n\n")
    o.write("## Top priority (P1/High) tasks — quick view\n\n")
    o.write("| Task ID | Title | Owner | Priority | Start | Due | Depends On |\n")
    o.write("|---|---|---|---|---|---|---|\n")
    for r in p1_tasks:
        tid = pick(r, ["taskid", "id", "task", "task_id"]) or "-"
        title = pick(r, ["task", "tasktitle", "title"]) or "-"
        owner = pick(r, ["owner"]) or "-"
        prio = pick(r, ["priority"]) or "-"
        start = pick(r, ["start", "started_at"]) or "-"
        due = pick(r, ["due", "done_at"]) or "-"
        depends = pick(r, ["dependson", "depends_on", "depends", "dependson"]) or "-"
        o.write(f"| {tid} | {title} | {owner} | {prio} | {start} | {due} | {depends} |\n")

print("Wrote", OUT)
