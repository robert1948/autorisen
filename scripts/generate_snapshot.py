#!/usr/bin/env python3
"""Generate a concise Markdown snapshot from docs/autorisen_project_plan.csv
Writes output to docs/Master_ProjectPlan.generated.md (non-destructive).
"""
import csv
from collections import Counter
from datetime import date

CSV = "docs/autorisen_project_plan.csv"
OUT = "docs/Master_ProjectPlan.generated.md"

with open(CSV, newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

status_counts = Counter(r["status"] for r in rows)
total = len(rows)

p1_tasks = [r for r in rows if r["priority"].strip().upper() == "P1"][:12]

today = date.today().isoformat()

with open(OUT, "w") as o:
    o.write("# Master Project Plan (generated snapshot) — autorisen\n\n")
    o.write("Snapshot: " + today + "\n\n")
    o.write("- Total tasks: " + str(total) + "\n")
    o.write("- Status counts: " + ", ".join(f"{k}: {v}" for k, v in status_counts.items()) + "\n\n")
    o.write("## Top priority (P1) tasks — quick view\n\n")
    o.write("| Task ID | Title | Owner | Estimate | Depends On |\n")
    o.write("|---|---|---:|---:|---:|\n")
    for r in p1_tasks:
        o.write(
            f"| {r['task_id']} | {r['task_title']} | {r['owner']} | {r['estimate']} | {r['depends_on']} |\n"
        )

print("Wrote", OUT)
