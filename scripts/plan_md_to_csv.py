#!/usr/bin/env python3
"""Extract the first Markdown table from a file and write it as CSV.
Usage: python scripts/plan_md_to_csv.py docs/Master_ProjectPlan.md > tasks.csv
"""
import csv
import re
import sys


def extract_first_table(lines):
    table = []
    in_table = False
    for line in lines:
        if re.match(r"\s*\|", line):
            # table-like line
            in_table = True
            table.append(line.strip())
        else:
            if in_table:
                break
    return table


def parse_md_table(table_lines):
    # Remove separator line (---|---) if present
    rows = [
        [cell.strip() for cell in re.split(r"\s*\|\s*", row.strip())[1:-1]]
        for row in table_lines
    ]
    if len(rows) >= 2 and re.match(r"^:?-+:?$", "".join(rows[1])):
        # naive detect, but leave as-is
        pass
    return rows


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: plan_md_to_csv.py <markdown-file>")
        sys.exit(2)
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    table_lines = extract_first_table(lines)
    if not table_lines:
        print("No markdown table found.", file=sys.stderr)
        sys.exit(1)
    rows = parse_md_table(table_lines)
    writer = csv.writer(sys.stdout)
    for r in rows:
        writer.writerow(r)
