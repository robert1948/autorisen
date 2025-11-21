import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.plan_utils import (  # noqa: E402
    PLAN_CSV,
    PLAN_HEADER,
    VALID_PHASES,
    VALID_STATUSES,
    load_plan_rows,
)

RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_PRIORITY = re.compile(r"^P\d$")


def test_csv_valid():
    assert PLAN_CSV.exists(), f"missing {PLAN_CSV}"
    header, rows = load_plan_rows(PLAN_CSV)
    assert header == PLAN_HEADER
    assert rows, "CSV empty?"

    seen_ids = set()
    for row in rows:
        assert row["id"], "missing required: id"
        assert row["phase"] in VALID_PHASES, f"unexpected phase: {row['phase']}"
        assert row["task"], "missing required: task"
        assert row["owner"], "missing required: owner"
        assert row["status"] in VALID_STATUSES, f"bad status: {row['status']}"
        assert row["priority"], "missing required: priority"
        assert RE_PRIORITY.match(row["priority"]), f"bad priority: {row['priority']}"

        completion = row.get("completion_date", "")
        if completion:
            assert RE_DATE.match(completion), f"bad completion_date: {completion}"

        hours = row.get("estimated_hours", "")
        if hours:
            assert hours.isdigit(), f"estimated_hours not numeric: {row['id']}"

        deps = row.get("dependencies", "")
        # allow empty dependencies but ensure we don't store whitespace-only garbage
        assert deps == deps.strip(), "dependencies has leading/trailing whitespace"

        assert row["id"] not in seen_ids, f"duplicate id detected: {row['id']}"
        seen_ids.add(row["id"])
