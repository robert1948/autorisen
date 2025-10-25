#!/usr/bin/env python3
"""
PlanSyncAgent helper.

- Treats docs/autorisen_project_plan.csv as source of truth for a task table.
- Reads/writes a fenced section in docs/Master_ProjectPlan.md between:
    <!-- PLAN:BEGIN -->
    <!-- PLAN:END -->
- --check-only exits non-zero if drift is detected (IDs/title/status mismatch).
- --apply regenerates the fenced table from CSV.

CSV requirements:
- Must include at least the columns: id, title
- Optional columns (if present) are included: status, owner, priority

This script is deliberately simple and deterministic.
"""
import csv
import re
import sys
from pathlib import Path

CSV_PATH = Path("docs/autorisen_project_plan.csv")
MD_PATH = Path("docs/Master_ProjectPlan.md")
BEGIN = "<!-- PLAN:BEGIN -->"
END = "<!-- PLAN:END -->"


def load_csv_rows():
    if not CSV_PATH.exists():
        print(f"[PlanSync] Missing {CSV_PATH}", file=sys.stderr)
        return []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    # Minimal validation
    for required in ("id", "title"):
        if required not in reader.fieldnames:
            print(
                f"[PlanSync] CSV missing required column: {required}", file=sys.stderr
            )
            sys.exit(2)
    return rows, reader.fieldnames


def extract_fenced(md_text: str):
    pattern = re.compile(
        rf"{re.escape(BEGIN)}(.*?){re.escape(END)}",
        flags=re.DOTALL,
    )
    m = pattern.search(md_text)
    if not m:
        return None, None, None
    return m.group(0), m.start(), m.end()


def render_table(rows, fieldnames):
    # choose columns to output
    base_cols = ["id", "title"]
    optional = [c for c in ("status", "owner", "priority") if c in fieldnames]
    cols = base_cols + optional

    # header
    header = "| " + " | ".join(c.capitalize() for c in cols) + " |\n"
    sep = "| " + " | ".join("---" for _ in cols) + " |\n"
    body = ""
    for r in rows:
        body += "| " + " | ".join((r.get(c, "") or "").strip() for c in cols) + " |\n"
    block = f"{BEGIN}\n\n{header}{sep}{body}\n{END}"
    return block


def parse_md_table(md_text: str):
    fenced, s, e = extract_fenced(md_text)
    if not fenced:
        return set(), None, None, None
    # Extract IDs from table lines
    lines = fenced.splitlines()
    ids = set()
    for ln in lines:
        if ln.strip().startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if cells and cells[0].lower() != "id" and cells[0] != "---":
                ids.add(cells[0])
    return ids, fenced, s, e


def main():
    check_only = "--check-only" in sys.argv
    apply = "--apply" in sys.argv

    rows_fieldnames = load_csv_rows()
    if not rows_fieldnames:
        # If CSV missing, consider no drift but warn
        print("[PlanSync] No CSV present; nothing to sync.")
        sys.exit(0)
    rows, fieldnames = rows_fieldnames

    if not MD_PATH.exists():
        # Create a stub MD with fenced section
        print(f"[PlanSync] {MD_PATH} not found, creating stub with fenced table.")
        MD_PATH.parent.mkdir(parents=True, exist_ok=True)
        MD_PATH.write_text(
            f"# Master Project Plan\n\n{render_table(rows, fieldnames)}\n",
            encoding="utf-8",
        )
        sys.exit(1 if check_only else 0)

    md_text = MD_PATH.read_text(encoding="utf-8")
    md_ids, fenced, s, e = parse_md_table(md_text)

    csv_ids = {r.get("id", "") for r in rows}
    # Quick drift checks (IDs)
    id_drift = md_ids != csv_ids

    # Re-render block from CSV for content drift detection
    regenerated = render_table(rows, fieldnames)
    content_drift = False
    if fenced and regenerated.strip() != regenerated.strip():
        # (Always false; we want to compare fenced vs regenerated)
        pass
    if fenced and fenced.strip() != regenerated.strip():
        content_drift = True

    if check_only:
        if id_drift or content_drift or not fenced:
            # Print a machine-readable diff summary
            added = sorted(list(csv_ids - md_ids))
            removed = sorted(list(md_ids - csv_ids)) if md_ids else []
            print("```diff")
            for a in added:
                print(f"+ ID {a}")
            for r in removed:
                print(f"- ID {r}")
            print("```")
            print("[PlanSync] Drift detected or fenced section missing.")
            sys.exit(1)
        print("[PlanSync] No drift.")
        sys.exit(0)

    if apply:
        # Insert or replace fenced section
        if fenced:
            new_md = md_text[:s] + regenerated + md_text[e:]
        else:
            # Append section at end
            new_md = md_text.rstrip() + "\n\n" + regenerated + "\n"
        MD_PATH.write_text(new_md, encoding="utf-8")
        print("[PlanSync] Applied regenerated table to Master_ProjectPlan.md")
        sys.exit(0)

    print("Usage: plan_sync.py --check-only | --apply", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
