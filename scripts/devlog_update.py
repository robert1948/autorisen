#!/usr/bin/env python3
"""Development log helper.

Usage (quick entry):
  python scripts/devlog_update.py --type refactor --scope auth --summary "migrate utc datetimes" --impact none --pr 123

Verify mode (CI):
  python scripts/devlog_update.py --verify

Adds or verifies a dated line in docs/DEVELOPMENT_LOG.md.
"""
from __future__ import annotations
import argparse
import datetime as dt
import pathlib
import re
import sys

LOG_PATH = pathlib.Path("docs/DEVELOPMENT_LOG.md")

QUICK_FMT = "{date} – [{type}] {summary} (PR #{pr}) – impact: {impact}"

CODE_PATH_PREFIXES = (
    "backend/app/",
    "backend/migrations",
    "client/src/",
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--type",
        dest="type_",
        help="feature|refactor|fix|infra|docs|perf|security",
        default=None,
    )
    p.add_argument("--scope", help="short scope label", default=None)
    p.add_argument("--summary", help="short summary", default=None)
    p.add_argument("--impact", help="api|db|perf|security|none", default="none")
    p.add_argument("--pr", help="PR number", default="?")
    p.add_argument(
        "--full", action="store_true", help="(reserved) future full template expansion"
    )
    p.add_argument(
        "--verify", action="store_true", help="Fail if required entry missing"
    )
    p.add_argument(
        "--auto",
        action="store_true",
        help="If verify fails, insert stub entry and exit 0",
    )
    p.add_argument(
        "--changed", nargs="*", help="Optional explicit changed files list (CI)."
    )
    return p.parse_args()


def read_log() -> list[str]:
    if not LOG_PATH.exists():
        print(f"ERROR: {LOG_PATH} missing", file=sys.stderr)
        return []
    return LOG_PATH.read_text(encoding="utf-8").splitlines()


def write_log(lines: list[str]):
    LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def has_today_entry(lines: list[str], today: str) -> bool:
    pattern = re.compile(rf"^{today} – ")
    return any(pattern.search(line) for line in lines)


def detect_needs_entry(changed_files: list[str]) -> bool:
    interesting = [
        p
        for p in changed_files
        if any(p.startswith(pref) for pref in CODE_PATH_PREFIXES)
    ]
    return len(interesting) > 0


def insert_quick_entry(lines: list[str], entry: str) -> list[str]:
    # Insert after first heading line (# Autorisen – Development Log)
    out: list[str] = []
    inserted = False
    for i, line in enumerate(lines):
        out.append(line)
        if not inserted and line.startswith("# Autorisen"):
            # Skip possible blank line(s) then insert
            # Ensure a blank line follows heading then our entry
            # Find next non-empty line index for correct placement
            inserted = True
            out.append("")
            out.append(entry)
            out.append("")
    if not inserted:  # fallback append
        out.insert(0, entry)
    return out


def main():
    args = parse_args()
    today = dt.date.today().isoformat()
    lines = read_log()

    if args.verify:
        # In verify mode we require that if code changed, today's entry exists
        # Accept changed list via args or git diff fallback
        if args.changed:
            changed = args.changed
        else:
            # Fallback: attempt to get diff vs origin/main
            try:
                import subprocess

                res = subprocess.run(
                    ["git", "fetch", "origin", "main"], capture_output=True
                )
                _ = res.returncode
                diff = subprocess.check_output(
                    ["git", "diff", "--name-only", "origin/main...HEAD"], text=True
                )
                changed = [l.strip() for l in diff.splitlines() if l.strip()]
            except Exception:
                changed = []
        if not detect_needs_entry(changed):
            print("No relevant code changes detected; skipping dev log enforcement.")
            return 0
        if has_today_entry(lines, today):
            print("Dev log entry present for today.")
            return 0
        if args.auto:
            stub = QUICK_FMT.format(
                date=today,
                type_="chore",
                type="chore",
                summary="auto-stub: fill details",
                pr="?",
                impact="none",
            )
            new_lines = insert_quick_entry(lines, stub)
            write_log(new_lines)
            print("Inserted stub dev log entry (auto mode).")
            return 0
        print("ERROR: Missing dev log entry for today.", file=sys.stderr)
        return 1

    # Non-verify mode (add/update)
    required = ["type_", "summary"]
    for r in required:
        if getattr(args, r) is None:
            print(
                f"Missing required --{r.replace('_','')} for log update",
                file=sys.stderr,
            )
            return 2

    entry = QUICK_FMT.format(
        date=today,
        type_=args.type_,
        type=args.type_,  # allow template variant
        summary=(f"{args.scope}: {args.summary}" if args.scope else args.summary),
        pr=args.pr,
        impact=args.impact,
    )

    if has_today_entry(lines, today):
        print("Entry for today already exists; not adding duplicate.")
        return 0

    new_lines = insert_quick_entry(lines, entry)
    write_log(new_lines)
    print("Inserted dev log entry:")
    print(entry)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
