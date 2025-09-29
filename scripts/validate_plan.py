#!/usr/bin/env python3
"""Lightweight validator for docs/autorisen_project_plan.csv

Checks:
 - header columns present and in-order
 - each task_id is unique
 - status is one of {todo,busy,done}
 - dates (started_at, updated_at, done_at) are either empty or YYYY-MM-DD
 - priority values look like P1/P2/etc.

Exit code 0 on success, non-zero on failure.
"""
from csv import DictReader
from collections import Counter
import re
import sys

import argparse

PATH = "docs/autorisen_project_plan.csv"

ARGP = argparse.ArgumentParser(description="Validate a canonical project plan CSV")
ARGP.add_argument(
    "path", nargs="?", help="Path to CSV to validate (defaults to docs/autorisen_project_plan.csv)"
)
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

EXPECTED_HEADER = [
    "module",
    "area",
    "task_id",
    "task_title",
    "description",
    "owner",
    "priority",
    "estimate",
    "depends_on",
    "status",
    "started_at",
    "updated_at",
    "done_at",
    "notes",
]

ok = True
args = ARGP.parse_args()
target = args.path or PATH

with open(target, newline="") as f:
    reader = DictReader(f)
    header = reader.fieldnames
    if header != EXPECTED_HEADER:
        print("ERROR: header mismatch")
        print("Expected:", EXPECTED_HEADER)
        print("Found:   ", header)
        ok = False

    rows = list(reader)

ids = [r["task_id"] for r in rows]
dups = [tid for tid, c in Counter(ids).items() if c > 1]
if dups:
    print("ERROR: duplicate task_id(s):", dups)
    ok = False

for i, r in enumerate(rows, start=1):
    status = r["status"].strip()
    if status not in ("todo", "busy", "done"):
        print(f"ERROR row {i} ({r['task_id']}): invalid status '{status}'")
        ok = False
    for col in ("started_at", "updated_at", "done_at"):
        v = r[col].strip()
        if v and not RE_DATE.match(v):
            print(f"ERROR row {i} ({r['task_id']}): malformed date in {col}: '{v}'")
            ok = False
    pr = r["priority"].strip()
    if pr and not re.match(r"^P\d+$", pr):
        print(f"ERROR row {i} ({r['task_id']}): malformed priority '{pr}'")
        ok = False

if not ok:
    sys.exit(2)
print("OK: validation passed")
