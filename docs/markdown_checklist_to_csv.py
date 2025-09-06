#!/usr/bin/env python3
"""
Convert a Markdown checklist (e.g., Checklist_MVP.md) into a CSV project plan.

Heuristics supported:
- Tasks lines: starting with "- [ ]" or "- [x]" / "* [ ]" / "* [x]"
- Status from checkbox: [ ] -> "To Do", [x]/[X] -> "Done"
- Category from nearest preceding Markdown heading (## or ###)
- Inline tags (optional, anywhere in the task line or trailing notes):
    - ID:            #MVP-123
    - Priority:      !high | !med | !low (also accepts !h !m !l)
    - Owner:         @robert (multiple owners supported, comma-joined)
    - Due date:      due: YYYY-MM-DD
    - Start date:    start: YYYY-MM-DD
    - Dependencies:  deps: MVP-001|MVP-002 (pipe or comma separated)
    - Deliverables:  deliver: some text here
    - Notes:         note: some text here
Anything not captured goes to Notes.
"""

import re
import csv
import sys
from pathlib import Path

COLUMNS = [
    "ID",
    "Task / Milestone",
    "Category",
    "Owner",
    "Priority",
    "Status",
    "Start Date",
    "Due Date",
    "Dependencies",
    "Deliverables",
    "Notes",
]

PRIORITY_MAP = {
    "high": "High",
    "h": "High",
    "med": "Medium",
    "m": "Medium",
    "low": "Low",
    "l": "Low",
}

def normalize_priority(token: str):
    token = token.strip().lower()
    return PRIORITY_MAP.get(token, token.title() if token else "")

def parse_line_tags(text: str):
    # Extract ID(s) like #MVP-001 (keep first as ID, additional go to Notes)
    ids = re.findall(r"#([A-Za-z0-9_-]+)", text)
    task_id = ids[0] if ids else ""

    # Priority: !high / !med / !low (or !h !m !l)
    prios = re.findall(r"!([A-Za-z]+)", text)
    priority = normalize_priority(prios[0]) if prios else ""

    # Owners: @name
    owners = re.findall(r"@([A-Za-z0-9._-]+)", text)
    owner = ", ".join(owners)

    # Dates: start: YYYY-MM-DD, due: YYYY-MM-DD
    start = ""
    due = ""
    m = re.search(r"\bstart:\s*(\d{4}-\d{2}-\d{2})\b", text, flags=re.IGNORECASE)
    if m: start = m.group(1)
    m = re.search(r"\bdue:\s*(\d{4}-\d{2}-\d{2})\b", text, flags=re.IGNORECASE)
    if m: due = m.group(1)

    # Dependencies: deps: a|b or a,b or space separated tokens with dash format
    deps = ""
    m = re.search(r"\bdeps?:\s*([^\s\]]+)", text, flags=re.IGNORECASE)
    if m:
        raw = m.group(1)
        deps = ", ".join([t for t in re.split(r"[|,]", raw) if t.strip()])

    # Deliverables: deliver: ... (greedy until note: or end)
    deliver = ""
    m = re.search(r"\bdeliver:\s*(.+?)(?=\s+\bnote:\b|$)", text, flags=re.IGNORECASE)
    if m:
        deliver = m.group(1).strip()

    # Notes: note: ... (greedy to end)
    notes = ""
    m = re.search(r"\bnote:\s*(.+)$", text, flags=re.IGNORECASE)
    if m:
        notes = m.group(1).strip()

    return task_id, priority, owner, start, due, deps, deliver, notes

def strip_tags(text: str):
    # Remove known inline metadata to leave the clean task title
    text = re.sub(r"#([A-Za-z0-9_-]+)", "", text)            # IDs
    text = re.sub(r"!([A-Za-z]+)", "", text)                 # priorities
    text = re.sub(r"@([A-Za-z0-9._-]+)", "", text)           # owners
    text = re.sub(r"\b(start|due|deps?|deliver|note):\s*[^]]+", "", text, flags=re.IGNORECASE)
    return " ".join(text.split())

def md_to_csv(md_path: Path, csv_path: Path):
    current_category = ""
    rows = []

    with md_path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip()

            # Track category from headings
            m = re.match(r"^\s*#{2,3}\s+(.*)", line)
            if m:
                current_category = m.group(1).strip()
                continue

            # Match task lines with checkbox
            m = re.match(r"^\s*[-*]\s*\[( |x|X)\]\s+(.*)$", line)
            if not m:
                continue

            status = "Done" if m.group(1).lower() == "x" else "To Do"
            body = m.group(2).strip()

            task_id, priority, owner, start, due, deps, deliver, notes = parse_line_tags(body)
            # Clean task title by removing inline tags
            clean_title = strip_tags(body)

            row = {
                "ID": task_id,
                "Task / Milestone": clean_title,
                "Category": current_category,
                "Owner": owner,
                "Priority": priority,
                "Status": status,
                "Start Date": start,
                "Due Date": due,
                "Dependencies": deps,
                "Deliverables": deliver,
                "Notes": notes,
            }
            rows.append(row)

    # Write CSV
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 markdown_checklist_to_csv.py /path/to/Checklist_MVP.md /path/to/output.csv")
        sys.exit(1)
    md_path = Path(sys.argv[1]).expanduser().resolve()
    csv_path = Path(sys.argv[2]).expanduser().resolve()
    if not md_path.exists():
        print(f"Error: Markdown file not found: {md_path}")
        sys.exit(2)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_to_csv(md_path, csv_path)
    print(f"✅ Wrote CSV: {csv_path}")

if __name__ == "__main__":
    main()
