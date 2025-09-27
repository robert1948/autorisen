import csv, datetime as dt, pathlib
p = pathlib.Path("docs/autorisen_project_plan.csv")
rows = []
today = dt.date.today().isoformat()
with p.open(newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    rows = list(r); hdr = r.fieldnames
for row in rows:
    if row.get("status") in {"todo","busy","done"}:
        row["updated_at"] = today if row.get("updated_at","") != today else row["updated_at"]
with p.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=hdr); w.writeheader(); w.writerows(rows)
print(f"Updated {p} on {today} (rows={len(rows)})")
