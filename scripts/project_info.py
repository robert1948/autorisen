#!/usr/bin/env python3
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path


def main():
    plan_path = Path("docs/project-plan.csv")
    if not plan_path.exists():
        print("⚠️  Plan file missing: docs/project-plan.csv")
        sys.exit(0)

    def rows_iter(path: Path):
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(
                row
                for row in handle
                if row.strip() and not row.lstrip().startswith("#")
            )
            for row in reader:
                if row.get("id"):
                    yield row

    rows = list(rows_iter(plan_path))
    if not rows:
        print("⚠️  Plan CSV has no task rows")
        sys.exit(0)

    status_counts = Counter(row["status"].strip().lower() for row in rows)
    total = len(rows)
    done = status_counts.get("done", 0) + status_counts.get("completed", 0)
    in_progress = status_counts.get("in-progress", 0) + status_counts.get("in review", 0)
    todo = status_counts.get("todo", 0) + status_counts.get("planned", 0)

    pct_done = (done / total) * 100 if total else 0

    print(
        "📈 Tasks: {} total | {} done | {} in-progress | {} planned".format(
            total, done, in_progress, todo
        )
    )
    print("✅ Completion: {:.1f}% of tasks".format(pct_done))

    priority_rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    active = [
        row
        for row in rows
        if row["status"].strip().lower() in {"in-progress", "in review", "todo", "planned"}
        and row.get("priority") in {"P0", "P1"}
    ]
    active.sort(
        key=lambda row: (
            priority_rank.get(row.get("priority"), 99),
            0 if row["status"] == "in-progress" else 1,
            row["id"],
        )
    )

    if active:
        print("🔥 High-priority queue:")
        for row in active[:5]:
            print(
                "   • {id} ({priority} {status}): {task} [{owner}]".format(
                    id=row["id"],
                    priority=row.get("priority", ""),
                    status=row["status"],
                    task=row["task"],
                    owner=row["owner"],
                )
            )
    else:
        print("🔥 High-priority queue: n/a")


if __name__ == "__main__":
    main()
