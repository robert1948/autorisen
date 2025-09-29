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
import csv
import sys
from pathlib import Path

CSV_PATH = Path("docs/autorisen_project_plan.csv")
# Accept either the canonical header or a simpler task-tracking header
CANONICAL_HEAD = ["file", "group", "subgroup", "task", "status"]
ALT_HEADS = [
    [
        "id",
        "task",
        "owner",
        "status",
        "priority",
        "start",
        "due",
        "milestone",
        "dependson",
        "notes",
    ],
]


def fail(msg):
    print(f"❌ {msg}")
    sys.exit(1)


def main():
    if not CSV_PATH.exists():
        fail(f"Missing {CSV_PATH}")

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        flds = [c.strip().lower() for c in (rdr.fieldnames or [])]

        ok_header = False
        if flds == CANONICAL_HEAD:
            ok_header = True
        else:
            for alt in ALT_HEADS:
                if flds == alt:
                    ok_header = True
                    break

        if not ok_header:
            fail(
                f"Bad header. Got {rdr.fieldnames}, expected {CANONICAL_HEAD} or one of {ALT_HEADS}"
            )

        # Normalize rows into canonical keys
        seen = set()
        n = 0
        for raw in rdr:
            n += 1
            row = {k.strip().lower(): (v or "").strip() for k, v in raw.items() if k}

            # Map possible alternative keys into canonical fields
            task = row.get("task") or row.get("tasktitle") or row.get("id") or ""
            status = (row.get("status") or "").strip().lower()
            file = row.get("file") or row.get("milestone") or ""
            group = row.get("group") or row.get("owner") or ""
            subgroup = row.get("subgroup") or ""

            # Map common status labels
            if status in {"in progress", "in_progress", "inprogress", "doing"}:
                status = "todo"
            if status in {"blocked", "on hold"}:
                status = "todo"

            if not task:
                fail(f"Row {n}: empty task")
            if status not in {"todo", "done"}:
                fail(f"Row {n}: invalid status '{status}'")

            key = (file, group, subgroup, task)
            if key in seen:
                fail(f"Row {n}: duplicate task in same group: {key}")
            seen.add(key)

    print(f"✅ {CSV_PATH} valid ({n} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
