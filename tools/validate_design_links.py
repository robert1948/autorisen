#!/usr/bin/env python3
"""Validate design playbooks to ensure links and code references stay healthy."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import sync_figma_components

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYBOOK_DIR = ROOT / "docs" / "playbooks" / "design"


def _matches(playbook_slug: str, target: str) -> bool:
    slug = playbook_slug.lower()
    target = target.lower().removesuffix(".md")
    return slug == target or slug.endswith(target)


def _check_file(path_str: str) -> bool:
    if not path_str:
        return False
    candidate = ROOT / path_str
    return candidate.exists()


def validate(playbook_paths, target_slug: str | None = None) -> int:
    errors: list[str] = []
    checked = 0

    for path in sorted(playbook_paths):
        playbook = sync_figma_components.parse_playbook(path)
        if target_slug and not _matches(playbook["slug"], target_slug):
            continue

        checked += 1
        figma_link = str(playbook.get("figma_link", "")).strip()
        if not figma_link or not figma_link.startswith("http"):
            errors.append(f"{playbook['path']}: missing or invalid Figma link")

        components = playbook.get("components", [])
        if not isinstance(components, list):
            errors.append(
                f"{playbook['path']}: unable to read component table (got {type(components).__name__})"
            )
            continue
        if not components:
            errors.append(f"{playbook['path']}: no component rows found")

        for component in components:
            file_path = str(component.get("file_path", "")).strip().strip("`")
            if not file_path:
                errors.append(
                    f"{playbook['path']}: empty file path for {component.get('figma_component')}"
                )
                continue
            if not _check_file(file_path):
                errors.append(
                    f"{playbook['path']}: file not found → {file_path} (component {component.get('figma_component')})"
                )

    if target_slug and checked == 0:
        errors.append(f"No playbook matched '{target_slug}'")

    if errors:
        for line in errors:
            print(f"✗ {line}", file=sys.stderr)
        return 1

    print(f"✓ Design playbooks validated ({checked} checked)")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate design playbooks and component links"
    )
    parser.add_argument(
        "--playbooks-dir",
        default=str(DEFAULT_PLAYBOOK_DIR),
        help="Directory containing design playbooks",
    )
    parser.add_argument(
        "--playbook",
        default="",
        help="Optional slug to validate a single playbook (e.g. 'auth-flow')",
    )
    args = parser.parse_args()

    playbook_dir = Path(args.playbooks_dir).resolve()
    if not playbook_dir.exists():
        raise SystemExit(f"Playbook directory not found: {playbook_dir}")

    playbook_paths = list(playbook_dir.glob("*.md"))
    if not playbook_paths:
        raise SystemExit(f"No playbooks found in {playbook_dir}")

    sys.exit(validate(playbook_paths, target_slug=args.playbook or None))


if __name__ == "__main__":
    main()
