import csv, re, pathlib
P = pathlib.Path("docs/autorisen_project_plan.csv")
RE_STATUS = {"todo","busy","done"}
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REQUIRED = ["module","task_id","task_title","owner","priority","estimate","status"]
def test_csv_valid():
    assert P.exists(), f"missing {P}"
    rows = list(csv.DictReader(P.open(encoding="utf-8")))
    assert rows, "CSV empty?"
    for r in rows:
        for k in REQUIRED:
            assert (r.get(k) or "").strip(), f"missing required: {k}"
        assert r["status"] in RE_STATUS, f"bad status: {r['status']}"
        for c in ("started_at","updated_at","done_at"):
            v = (r.get(c) or "").strip()
            if v: assert RE_DATE.match(v), f"{c} not ISO date: {v}"
