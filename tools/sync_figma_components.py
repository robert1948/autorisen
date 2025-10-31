#!/usr/bin/env python3
"""Aggregate design playbooks into a component inventory.

The script reads markdown playbooks under ``docs/playbooks/design`` and
collects metadata plus the component mapping table.  The resulting
inventory is written to JSON so other tooling (or CI) can reason about
which React files map to Figma components.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYBOOK_DIR = ROOT / "docs" / "playbooks" / "design"
DEFAULT_OUTPUT = ROOT / "docs" / "figma" / "component_inventory.json"

_META_PATTERNS = {
    "owner": re.compile(r"\*\*Owner:\*\*\s*(.+)", re.IGNORECASE),
    "figma_link": re.compile(
        r"\*\*Figma Link:\*\*\s*\[[^\]]+\]\(([^)]+)\)", re.IGNORECASE
    ),
    "status": re.compile(r"\*\*Status:\*\*\s*(.+)", re.IGNORECASE),
    "purpose": re.compile(r"\*\*Purpose:\*\*\s*(.+)", re.IGNORECASE),
}


def _parse_component_rows(lines: List[str], start_index: int) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    # Skip header and delimiter row (start_index is header line)
    index = start_index + 2
    while index < len(lines):
        row = lines[index].strip()
        if not row.startswith("|"):
            break
        cells = [cell.strip() for cell in row.split("|")[1:-1]]
        if len(cells) >= 4 and not set(cells[0]) <= {"-"}:
            rows.append(
                {
                    "figma_component": cells[0],
                    "react_component": cells[1],
                    "file_path": cells[2].strip("`"),
                    "status": cells[3],
                }
            )
        index += 1
    return rows


def parse_playbook(path: Path) -> Dict[str, object]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = next(
        (line[2:].strip() for line in lines if line.startswith("# ")), path.stem
    )

    metadata: Dict[str, str] = {}
    for key, pattern in _META_PATTERNS.items():
        match = pattern.search(text)
        if match:
            metadata[key] = match.group(1).strip()

    component_rows: List[Dict[str, str]] = []
    for idx, line in enumerate(lines):
        if line.strip().startswith("|") and "Figma Component" in line:
            component_rows = _parse_component_rows(lines, idx)
            break

    return {
        "path": str(path.relative_to(ROOT)),
        "slug": path.stem,
        "title": title,
        "owner": metadata.get("owner", ""),
        "figma_link": metadata.get("figma_link", ""),
        "status": metadata.get("status", ""),
        "purpose": metadata.get("purpose", ""),
        "components": component_rows,
    }


def collect_playbooks(paths: Iterable[Path]) -> List[Dict[str, object]]:
    return [parse_playbook(path) for path in sorted(paths)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate design playbooks into JSON inventory"
    )
    parser.add_argument(
        "--board", default="", help="Optional Figma board URL for reference"
    )
    parser.add_argument(
        "--playbooks-dir",
        default=str(DEFAULT_PLAYBOOK_DIR),
        help="Directory containing design playbooks (markdown)",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Where to write the aggregated JSON output",
    )
    args = parser.parse_args()

    playbook_dir = Path(args.playbooks_dir).resolve()
    if not playbook_dir.exists():
        raise SystemExit(f"Playbook directory not found: {playbook_dir}")

    playbooks = list(playbook_dir.glob("*.md"))
    if not playbooks:
        raise SystemExit(f"No playbooks found in {playbook_dir}")

    inventory = {
        "board": args.board,
        "playbooks": collect_playbooks(playbooks),
    }

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")

    total_components = sum(len(pb["components"]) for pb in inventory["playbooks"])
    print(
        f"✓ Wrote {output_path.relative_to(ROOT)} ({len(playbooks)} playbook(s), {total_components} component(s))"
    )
    if args.board:
        print(f"  Linked Figma board: {args.board}")


if __name__ == "__main__":
    main()
