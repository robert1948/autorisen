#!/usr/bin/env python3
"""Convert a human-friendly project plan CSV into the canonical schema.

Usage:
  python3 tools/csv_to_canonical.py --in docs/autorisen_project_plan.csv --out docs/autorisen_project_plan.csv

This script is conservative: it maps common columns into the canonical header used by
`scripts/validate_plan.py`. Fields not present are left empty or filled with reasonable defaults.
"""
import csv
from pathlib import Path
from datetime import date
import argparse

CANONICAL = [
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

ARG_PARSER = argparse.ArgumentParser()
ARG_PARSER.add_argument("--in", dest="infile", required=True)
ARG_PARSER.add_argument("--out", dest="outfile", required=True)


def normalize_row(raw):
    # map lowercase keys without spaces/underscores
    mapped = {
        (k or "").strip().lower().replace(" ", "").replace("_", ""): (v or "").strip()
        for k, v in raw.items()
        if k
    }

    # source columns we expect
    tid = mapped.get("id") or mapped.get("taskid") or mapped.get("task")
    title = mapped.get("task") or mapped.get("tasktitle") or tid
    owner = mapped.get("owner") or ""
    status = (mapped.get("status") or "").strip().lower()
    priority = (mapped.get("priority") or "").strip()
    start = mapped.get("start") or mapped.get("started_at") or ""
    due = mapped.get("due") or mapped.get("done_at") or ""
    milestone = mapped.get("milestone") or ""
    depends = mapped.get("dependson") or mapped.get("depends_on") or mapped.get("depends") or ""
    notes = mapped.get("notes") or ""
    description = mapped.get("description") or ""

    # Map status variants into canonical 'todo'|'done'
    if status in {"done", "complete", "closed"}:
        status_c = "done"
    else:
        # treat everything else as todo for now
        status_c = "todo"

    today = date.today().isoformat()

    # Normalize priority: accept P# or map human labels
    pr = ""
    if priority:
        p_low = priority.lower()
        if p_low.startswith("p") and p_low[1:].isdigit():
            pr = priority.upper()
        else:
            mapping = {"high": "P1", "medium": "P2", "low": "P3", "critical": "P0"}
            pr = mapping.get(p_low, "")

    out = {
        "module": milestone,
        "area": "",
        "task_id": tid or "",
        "task_title": title or "",
        "description": description,
        "owner": owner,
        "priority": pr,
        "estimate": "",
        "depends_on": depends,
        "status": status_c,
        "started_at": start,
        "updated_at": today,
        "done_at": due if status_c == "done" else "",
        "notes": notes,
    }
    return out


def convert(infile: str, outfile: str):
    p = Path(infile)
    if not p.exists():
        raise SystemExit(f"Input file not found: {infile}")

    with p.open(newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        rows = [normalize_row(r) for r in rdr]

    outp = Path(outfile)
    with outp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CANONICAL)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print("Wrote", outfile)


if __name__ == "__main__":
    args = ARG_PARSER.parse_args()
    convert(args.infile, args.outfile)
