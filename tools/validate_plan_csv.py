#!/usr/bin/env python3
"""Validate the canonical project plan CSV for structure and status values."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


REQUIRED_HEADER = ["file", "group", "subgroup", "task", "status"]
VALID_STATUSES = {"todo", "doing", "blocked", "review", "done"}


def validate(path: Path) -> int:
    if not path.exists():
        print(f"❌ Missing plan file: {path}")
        return 1

    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        if header != REQUIRED_HEADER:
            print("❌ Invalid header. Expected:", ",".join(REQUIRED_HEADER))
            print("   Found:", ",".join(header))
            return 1

        errors = 0
        for idx, row in enumerate(reader, start=2):
            status = row.get("status", "")
            if status not in VALID_STATUSES:
                print(f"❌ Row {idx}: invalid status '{status}'.")
                errors += 1
            for key in REQUIRED_HEADER:
                value = (row.get(key, "") or "").strip()
                if not value:
                    print(f"❌ Row {idx}: '{key}' column is empty.")
                    errors += 1

        if errors:
            return 1

    print(f"✅ {path} is valid.")
    return 0


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path("data/plan.csv")
    return validate(path)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
