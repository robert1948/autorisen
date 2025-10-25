#!/usr/bin/env python3
"""Generate the aggregated playbook overview table."""

from __future__ import annotations

import pathlib
import re
import textwrap
from typing import Dict, Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAYBOOK_DIR = ROOT / "docs" / "playbooks"
OUTPUT_PATH = ROOT / "docs" / "PLAYBOOKS_OVERVIEW.md"

CARD_PATTERN = re.compile(
    r"#\s*Playbook\s*(?P<num>\d+):\s*(?P<title>.+?)\s+"
    r"\*\*Owner\*\*:\s*(?P<owner>.+?)\s+"
    r"\*\*Supporting Agents\*\*:\s*(?P<agents>.+?)\s+"
    r"\*\*Status\*\*:\s*(?P<status>.+?)\s+"
    r"\*\*Priority\*\*:\s*(?P<priority>.+?)\s+",
    flags=re.IGNORECASE | re.DOTALL,
)


def parse_playbook(path: pathlib.Path) -> Optional[Dict[str, str]]:
    """Extract the metadata table row for a playbook markdown file."""

    match = CARD_PATTERN.search(path.read_text(encoding="utf-8"))
    if not match:
        return None

    record = match.groupdict()
    record["file"] = path.relative_to(ROOT).as_posix()
    return record


def main():
    rows: list[Dict[str, str]] = []
    for candidate in sorted(PLAYBOOK_DIR.glob("playbook-*.md")):
        if not candidate.is_file():
            continue
        parsed = parse_playbook(candidate)
        if parsed:
            rows.append(parsed)

    rows.sort(key=lambda row: int(row["num"]))

    table_lines = [
        "| # | Title | Owner | Status | Priority | File |",
        "|---:|---|---|---|---|---|",
    ]
    for row in rows:
        table_lines.append(
            f'| {row["num"]} | {row["title"]} | {row["owner"]} | '
            f'{row["status"]} | {row["priority"]} | `{row["file"]}` |'
        )

    next_steps = textwrap.dedent(
        """\
    ## ✅ Next Steps
    1. Keep this index synced as playbook statuses change.
    2. Ensure every new commit touching playbooks updates this table.
    3. Add Phase 3 playbooks (Marketplace, Payments) once MVP stabilization is complete.
    """
    )

    OUTPUT_PATH.write_text(
        "# Playbooks Overview\n\n"
        + "\n".join(table_lines)
        + "\n\n"
        + next_steps
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
