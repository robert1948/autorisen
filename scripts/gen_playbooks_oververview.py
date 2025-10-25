#!/usr/bin/env python3
"""
Generate docs/PLAYBOOKS_OVERVIEW.md with status summary + progress stats
"""

from __future__ import annotations
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOKS_DIR = ROOT / "docs" / "playbooks"
OUT = ROOT / "docs" / "PLAYBOOKS_OVERVIEW.md"

TITLE_RE = re.compile(r"^#\s*Playbook\s*[–-]\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
OWNER_RE = re.compile(r"^\*\*Owner\*\*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
AGENTS_RE = re.compile(
    r"^\*\*Supporting Agents\*\*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE
)
STATUS_RE = re.compile(
    r"^\*\*Status\*\*:\s*(Todo|Doing|Blocked|Done|Planned)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
PRIORITY_RE = re.compile(
    r"^\*\*Priority\*\*:\s*(P0|P1|P2)\s*$", re.IGNORECASE | re.MULTILINE
)

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}
STATUS_ORDER = {"Doing": 0, "Todo": 1, "Blocked": 2, "Planned": 3, "Done": 4}


def parse_playbook(md_path: Path) -> Dict[str, str] | None:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    title = TITLE_RE.search(text)
    owner = OWNER_RE.search(text)
    agents = AGENTS_RE.search(text)
    status = STATUS_RE.search(text)
    priority = PRIORITY_RE.search(text)

    if not title:
        first_h1 = re.search(r"^#\s*(.+)$", text, re.MULTILINE)
        if not first_h1:
            return None
        title = first_h1

    return {
        "title": title.group(1).strip(),
        "owner": owner.group(1).strip() if owner else "—",
        "agents": agents.group(1).strip() if agents else "—",
        "status": status.group(1).strip().title() if status else "Todo",
        "priority": priority.group(1).strip().upper() if priority else "P1",
        "file": str(md_path.relative_to(ROOT)).replace("\\", "/"),
    }


def summarize(rows: List[Dict[str, str]]) -> Tuple[str, float]:
    counts = Counter(r["status"] for r in rows)
    total = len(rows)
    done = counts.get("Done", 0)
    pct = (done / total * 100) if total else 0

    summary_lines = [
        "## 📊 Summary\n",
        f"**Total Playbooks:** {total}",
        f"**Done:** {done} | **Doing:** {counts.get('Doing',0)} | "
        f"**Todo/Planned:** {counts.get('Todo',0) + counts.get('Planned',0)} | **Blocked:** {counts.get('Blocked',0)}",
        f"**Overall Progress:** {done}/{total} ({pct:.0f}%)\n",
    ]
    return "\n".join(summary_lines), pct


def main() -> int:
    if not PLAYBOOKS_DIR.exists():
        print(f"[warn] Missing {PLAYBOOKS_DIR}")
        return 0

    rows = []
    for p in sorted(PLAYBOOKS_DIR.glob("*.md")):
        data = parse_playbook(p)
        if data:
            rows.append(data)

    rows.sort(
        key=lambda r: (
            PRIORITY_ORDER.get(r["priority"], 9),
            STATUS_ORDER.get(r["status"], 9),
            r["title"].lower(),
        )
    )

    summary, pct = summarize(rows)

    lines = []
    lines.append("# Playbooks Overview\n")
    lines.append(summary)
    lines.append("| # | Title | Owner | Status | Priority | File |")
    lines.append("|---:|---|---|---|:---:|---|")

    for i, r in enumerate(rows, 1):
        lines.append(
            f"| {i:02d} | {r['title']} | {r['owner']} | {r['status']} | {r['priority']} | `{r['file']}` |"
        )

    lines.append("\n## ✅ Next Steps")
    lines.append("1. Keep this index synced as playbook statuses change.")
    lines.append(
        "2. Each commit touching a playbook should re-generate this file (`make playbook-overview`)."
    )
    lines.append(
        "3. Track Done/Total ratios weekly; aim for 100% before production hand-off.\n"
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] Updated {OUT} ({pct:.0f}% complete)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
