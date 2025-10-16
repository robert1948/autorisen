# Templates & helper scripts

This folder contains templates and a small helper script to export the "Work breakdown" table to CSV.

- `docs/templates/Master_ProjectPlan.md.tpl` — master project plan template
- `docs/templates/project_status_report.md.tpl` — status report template
- `docs/templates/tasks_template.csv` — CSV template for tasks

## CSV helper

Run:

```bash
python3 scripts/plan_md_to_csv.py docs/Master_ProjectPlan.md > docs/tasks_export.csv
```

This extracts the first markdown table found in `docs/Master_ProjectPlan.md` and writes it to `docs/tasks_export.csv`.
