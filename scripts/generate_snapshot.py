#!/usr/bin/env python3
"""Generate a concise Markdown snapshot from docs/autorisen_project_plan.csv."""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.plan_utils import PLAN_CSV, load_plan_rows  # noqa: E402

OUT = "docs/Master_ProjectPlan.generated.md"

header, rows = load_plan_rows(PLAN_CSV)
status_counts = Counter(r["status"] for r in rows)
total = len(rows)
p1_tasks = [r for r in rows if r["priority"].upper() == "P1"][:12]
today = date.today().isoformat()

with open(OUT, "w", encoding="utf-8") as handle:
    handle.write("# Master Project Plan (generated snapshot) — autorisen\n\n")
    handle.write(f"Snapshot: {today}\n\n")
    handle.write(f"- Total tasks: {total}\n")
    handle.write(
        "- Status counts: "
        + ", ".join(f"{key}: {value}" for key, value in status_counts.items())
        + "\n\n"
    )
    handle.write("## Top priority (P1) tasks — quick view\n\n")
    handle.write("| Task ID | Task | Owner | Estimate (hrs) | Dependencies |\n")
    handle.write("|---|---|---|---:|---|\n")
    for row in p1_tasks:
        handle.write(
            f"| {row['id']} | {row['task']} | {row['owner']} | "
            f"{row['estimated_hours']} | {row['dependencies']} |\n"
        )

print("Wrote", OUT)
