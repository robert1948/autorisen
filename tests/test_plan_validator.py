import csv
import re

RE_STATUS = {"todo", "busy", "done"}
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REQUIRED = ["module", "task_id", "task_title", "owner", "priority", "estimate", "status"]


def rows(path="docs/autorisen_project_plan.csv"):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate(r):
    for k in REQUIRED:
        assert r.get(k, "").strip(), f"missing required: {k}"
    assert r["status"] in RE_STATUS, f"bad status: {r['status']}"
    for c in ("started_at", "updated_at", "done_at"):
        v = (r.get(c) or "").strip()
        if v:
            assert RE_DATE.match(v), f"{c} not ISO date: {v}"


def test_csv_valid():
    rs = rows()
    assert rs, "CSV empty?"
    for r in rs:
        validate(r)
