"""Guard test to prevent reintroduction of deprecated datetime.utcnow() in API routes.

This test scans the backend/app/routes directory (and optionally selected service layers later)
and fails if any usage of datetime.utcnow( is detected. The central approved replacement is
app.utils.datetime.utc_now().

If you need a naive UTC timestamp for a DB default, prefer timezone-aware handling or explicitly
justify with a noqa comment and update the allowlist mechanism below.
"""

from __future__ import annotations

import re
from pathlib import Path

# Directories to scan (extend later for services/models when migration completes)
SCAN_DIRS = [Path(__file__).parent.parent / "app" / "routes"]

# Allowlist patterns (file-relative substrings) that may legitimately contain the string
ALLOWLIST: list[tuple[str, str]] = [
    # (relative_path, justification)
]

UTCNOW_PATTERN = re.compile(r"datetime\.utcnow\(")


def _is_allowlisted(file_path: Path) -> bool:
    rel = file_path.relative_to(Path(__file__).parent.parent)
    rel_str = str(rel)
    return any(rel_str == entry[0] for entry in ALLOWLIST)


def test_no_datetime_utcnow_in_routes():
    violations: list[str] = []
    for base in SCAN_DIRS:
        for path in base.rglob("*.py"):
            if _is_allowlisted(path):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "datetime.utcnow(" in text:
                # Collect line numbers for clarity
                for idx, line in enumerate(text.splitlines(), start=1):
                    if "datetime.utcnow(" in line:
                        violations.append(f"{path}:L{idx}: {line.strip()}")
    assert not violations, (
        "Forbidden usage of datetime.utcnow() detected. Use app.utils.datetime.utc_now() instead.\n"
        + "\n".join(violations)
    )
