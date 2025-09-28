# tools/snapshot_plan.py
"""
Build docs/autorisen_project_plan.csv from Markdown checklists in docs/.
- Parses lines like: "- [ ] Do thing" or "- [x] Done thing"
- Keeps section headings as "group"
- Writes only if output changed (so the GH Action won't open a PR if nothing changed)
"""
from __future__ import annotations
import csv
import hashlib
import re
from pathlib import Path

DOCS = Path("docs")
OUT = DOCS / "autorisen_project_plan.csv"
CHECKBOX = re.compile(r"^\s*-\s*\[( |x)\]\s*(.+?)\s*$", re.I)
H1 = re.compile(r"^\s*#\s+(.+?)\s*$")
H2 = re.compile(r"^\s*##\s+(.+?)\s*$")


def read_markdown_tasks():
    items = []
    if not DOCS.exists():
        return items
    for md in sorted(DOCS.glob("*.md")):
        group1 = group2 = None
        for line in md.read_text(encoding="utf-8", errors="ignore").splitlines():
            m1 = H1.match(line)
            if m1:
                group1, group2 = m1.group(1).strip(), None
                continue
            m2 = H2.match(line)
            if m2:
                group2 = m2.group(1).strip()
                continue
            m = CHECKBOX.match(line)
            if m:
                done = m.group(1).lower() == "x"
                text = m.group(2).strip()
                items.append(
                    {
                        "file": md.name,
                        "group": group1 or "",
                        "subgroup": group2 or "",
                        "task": text,
                        "status": "done" if done else "todo",
                    }
                )
    return items


def build_csv_content(rows):
    # header is stable; no timestamps so content only changes when tasks change
    out_lines = []
    header = ["file", "group", "subgroup", "task", "status"]
    out_lines.append(",".join(header))
    for r in rows:
        # naive CSV escaping (csv module for correctness)
        pass
    # Use csv writer to ensure proper quoting
    from io import StringIO

    buf = StringIO()
    w = csv.DictWriter(buf, fieldnames=header)
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue().encode("utf-8")


def main():
    rows = read_markdown_tasks()
    content = build_csv_content(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    old = OUT.read_bytes() if OUT.exists() else b""
    if hashlib.sha256(old).hexdigest() != hashlib.sha256(content).hexdigest():
        OUT.write_bytes(content)
        print(f"wrote: {OUT} ({len(rows)} rows)")
    else:
        print("no changes; up to date")


if __name__ == "__main__":
    main()
