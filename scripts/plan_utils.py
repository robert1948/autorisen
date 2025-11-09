#!/usr/bin/env python3
"""Shared helpers for working with docs/autorisen_project_plan.csv."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

PLAN_CSV = Path("docs/autorisen_project_plan.csv")
PLAN_HEADER = [
    "id",
    "phase",
    "task",
    "owner",
    "status",
    "priority",
    "dependencies",
    "estimated_hours",
    "completion_date",
    "artifacts",
    "verification",
    "notes",
    "codex_hints",
]
VALID_PHASES = {
    "foundation",
    "agents",
    "payments",
    "optimization",
    "business",
    "maintenance",
}
VALID_STATUSES = {"todo", "in-progress", "completed", "blocked", "deferred"}


def _iter_clean_lines(path: Path) -> Iterator[str]:
    """Yield only CSV data rows (skip comments/blank lines)."""
    with path.open(encoding="utf-8", newline="") as handle:
        for raw in handle:
            if not raw.strip():
                continue
            if raw.lstrip().startswith("#"):
                continue
            yield raw


def load_plan_rows(path: Path = PLAN_CSV) -> tuple[list[str], list[dict[str, str]]]:
    """
    Return (header, rows) for the active project plan.

    - Ensures the CSV header matches PLAN_HEADER.
    - Strips whitespace from values.
    - Ignores any archived rows that don't map to a known phase.
    """
    if not path.exists():
        raise FileNotFoundError(path)

    reader = csv.DictReader(_iter_clean_lines(path))
    header = reader.fieldnames or []
    if header != PLAN_HEADER:
        raise ValueError(
            f"Unexpected header in {path}: {header}. Expected {PLAN_HEADER}."
        )

    rows: list[dict[str, str]] = []
    for raw_row in reader:
        normalized = {key: (raw_row.get(key) or "").strip() for key in PLAN_HEADER}
        phase = normalized.get("phase", "")
        if phase not in VALID_PHASES:
            continue
        rows.append(normalized)
    return header, rows
