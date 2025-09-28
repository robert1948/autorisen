# tools/validate_plan_csv.py
"""
Validate docs/autorisen_project_plan.csv
Rules:
- Must exist
- Header = file,group,subgroup,task,status
- status in {"todo","done"}
- task non-empty
- No duplicate (file, group, subgroup, task)
Prints a short report; exits 0 on pass, 1 on fail.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path

CSV_PATH = Path("docs/autorisen_project_plan.csv")
HEAD = ["file", "group", "subgroup", "task", "status"]


def fail(msg):
    print(f"❌ {msg}")
    sys.exit(1)


def main():
    if not CSV_PATH.exists():
        fail(f"Missing {CSV_PATH}")

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        if rdr.fieldnames != HEAD:
            fail(f"Bad header. Got {rdr.fieldnames}, expected {HEAD}")

        seen = set()
        n = 0
        for row in rdr:
            n += 1
            status = (row["status"] or "").strip().lower()
            task = (row["task"] or "").strip()
            key = (row["file"], row["group"], row["subgroup"], task)
            if not task:
                fail(f"Row {n}: empty task")
            if status not in {"todo", "done"}:
                fail(f"Row {n}: invalid status '{status}'")
            if key in seen:
                fail(f"Row {n}: duplicate task in same group: {key}")
            seen.add(key)

    print(f"✅ {CSV_PATH} valid ({n} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
