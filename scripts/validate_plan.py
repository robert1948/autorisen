#!/usr/bin/env python3
"""Lightweight validator for docs/autorisen_project_plan.csv."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.plan_utils import (
    PLAN_CSV,
    PLAN_HEADER,
    VALID_STATUSES,
    load_plan_rows,
)

RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_PRIORITY = re.compile(r"^P\d$")


def main() -> int:
    try:
        header, rows = load_plan_rows(PLAN_CSV)
    except FileNotFoundError:
        print(f"ERROR: missing {PLAN_CSV}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if header != PLAN_HEADER:
        print("ERROR: unexpected header layout", file=sys.stderr)
        return 2
    if not rows:
        print("ERROR: plan CSV contains no active rows", file=sys.stderr)
        return 2

    ok = True
    seen_ids: set[str] = set()
    for row in rows:
        task_id = row["id"]
        if not task_id:
            print("ERROR: row missing id", file=sys.stderr)
            ok = False
            continue
        if task_id in seen_ids:
            print(f"ERROR: duplicate id detected: {task_id}", file=sys.stderr)
            ok = False
        seen_ids.add(task_id)

        status = row["status"]
        if status not in VALID_STATUSES:
            print(f"ERROR {task_id}: invalid status '{status}'", file=sys.stderr)
            ok = False

        completion = row.get("completion_date", "")
        if completion and not RE_DATE.match(completion):
            print(
                f"ERROR {task_id}: completion_date not ISO ({completion})",
                file=sys.stderr,
            )
            ok = False

        priority = row.get("priority", "")
        if priority and not RE_PRIORITY.match(priority):
            print(f"ERROR {task_id}: malformed priority '{priority}'", file=sys.stderr)
            ok = False

        hours = row.get("estimated_hours", "")
        if hours and not hours.isdigit():
            print(f"ERROR {task_id}: estimated_hours not numeric '{hours}'", file=sys.stderr)
            ok = False

    if not ok:
        return 2

    print("OK: validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
