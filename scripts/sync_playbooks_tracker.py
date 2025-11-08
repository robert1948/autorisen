#!/usr/bin/env python3
"""Sync docs derived from PROJECT_PLAYBOOK_TRACKER.csv."""

from __future__ import annotations

import csv
import io
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "docs" / "PROJECT_PLAYBOOK_TRACKER.csv"
TRACKER_MD = ROOT / "docs" / "PROJECT_PLAYBOOK_TRACKER.md"
PLAYBOOKS_OVERVIEW = ROOT / "docs" / "PLAYBOOKS_OVERVIEW.md"

STATUS_DISPLAY = {
    "completed": "✅ Completed",
    "in-progress": "🚧 In Progress",
    "doing": "🚧 In Progress",
    "todo": "🕐 Todo",
    "planned": "🕐 Planned",
    "recurring": "🔁 Recurring",
}

BUCKET_LABELS = [
    ("✅ Completed", {"completed"}),
    ("🚧 In Progress", {"in-progress", "doing"}),
    ("🕐 Todo / Planned", {"todo", "planned"}),
    ("🔁 Recurring", {"recurring"}),
]


def _load_rows() -> list[dict[str, str]]:
    if not CSV_PATH.exists():
        raise SystemExit(f"Missing source CSV: {CSV_PATH}")

    filtered: list[str] = []
    with CSV_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            filtered.append(line)

    reader = csv.DictReader(io.StringIO("".join(filtered)))
    rows = [
        {(k or "").strip(): (v or "").strip() for k, v in row.items()}
        for row in reader
    ]
    return rows


def _bucket_rows(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        status = row.get("status", "").lower()
        normalized = status or "todo"
        if normalized not in {"completed", "in-progress", "doing", "todo", "planned", "recurring"}:
            normalized = "todo"
        buckets[normalized].append(row)
    return buckets


def _format_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "_None_\n"
    header = "| ID | Task | Owner | Priority | Status | Updated |\n|---|---|---|---|---|---|"
    lines = [header]
    for row in rows:
        updated = row.get("completion_date") or row.get("notes") or "—"
        status_key = row.get("status", "").lower()
        status = STATUS_DISPLAY.get(status_key, row.get("status", ""))
        lines.append(
            f"| {row.get('id','')} | {row.get('task','')} | {row.get('owner','')} | "
            f"{row.get('priority','')} | {status} | {updated} |"
        )
    return "\n".join(lines) + "\n"


def write_tracker(rows: list[dict[str, str]]) -> None:
    buckets = _bucket_rows(rows)
    counts = Counter(row.get("status", "").lower() or "todo" for row in rows)

    summary_lines = [
        "# Project Playbook Tracker",
        "",
        f"Source of truth: `{CSV_PATH.relative_to(ROOT)}`",
        "",
        "## Status Summary",
    ]
    for label, keys in BUCKET_LABELS:
        count = sum(counts.get(key, 0) for key in keys)
        summary_lines.append(f"- {label}: **{count}**")
    summary_lines.append("")

    for label, keys in BUCKET_LABELS:
        collected: list[dict[str, str]] = []
        for key in keys:
            collected.extend(sorted(buckets.get(key, []), key=lambda r: r.get("id", "")))
        summary_lines.append(f"## {label}")
        summary_lines.append("")
        summary_lines.append(_format_table(collected))

    TRACKER_MD.write_text("\n".join(summary_lines).rstrip() + "\n", encoding="utf-8")


def write_playbooks_overview(rows: list[dict[str, str]]) -> None:
    table_lines = [
        "# Playbooks Overview",
        "",
        "| ID | Title / Task | Status | Updated |",
        "|---|---|---|---|",
    ]
    for row in rows:
        status_key = row.get("status", "").lower()
        status = STATUS_DISPLAY.get(status_key, row.get("status", ""))
        updated = row.get("completion_date") or row.get("notes") or "—"
        table_lines.append(
            f"| {row.get('id','')} | {row.get('task','')} | {status} | {updated} |"
        )

    table_lines.extend(
        [
            "",
            "## ✅ Next Steps",
            "1. Keep this index synced as playbook statuses change.",
            "2. Ensure every new commit touching playbooks updates this table.",
            "3. Add Phase 3 playbooks (Marketplace, Payments) once MVP stabilization is complete.",
        ]
    )

    PLAYBOOKS_OVERVIEW.write_text("\n".join(table_lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    rows = _load_rows()
    write_tracker(rows)
    write_playbooks_overview(rows)


if __name__ == "__main__":
    main()
