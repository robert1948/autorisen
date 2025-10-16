#!/usr/bin/env python3
"""
Minimal snapshot generator.

Writes docs/autorisen_project_plan.csv with the expected header.
Enhance later to collect tasks from the repo.
"""
from pathlib import Path
import csv

out = Path("docs/autorisen_project_plan.csv")
out.parent.mkdir(parents=True, exist_ok=True)

with out.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["file", "group", "subgroup", "task", "status"])

print(f"Wrote {out}")
