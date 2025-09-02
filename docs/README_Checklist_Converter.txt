Markdown Checklist → CSV Converter

Files created:
- markdown_checklist_to_csv.py : Python script to convert your Checklist_MVP.md into a CSV.
- ProjectPlan_MVP.csv : You can choose any output path; example below uses your docs folder.

How to use on your machine:
1) Download the script.
2) Run:
   python3 markdown_checklist_to_csv.py "/home/robert/Development/autorisen/docs/Checklist_MVP.md" "/home/robert/Development/autorisen/docs/ProjectPlan_MVP.csv"

Task syntax in Markdown (examples):
- [ ] Implement login flow @robert !high #MVP-002 due: 2025-09-10 deps: MVP-001 deliver: working auth note: wire to frontend
- [x] Set up Docker + PostgreSQL @team !med #MVP-001 start: 2025-08-20 due: 2025-08-23

Rules:
- Category is taken from the nearest preceding heading (## or ###).
- Status is inferred from the checkbox [ ] (To Do) or [x] (Done).
- Optional inline tags:
    #MVP-123    -> ID
    !high/!med/!low (or !h/!m/!l) -> Priority
    @name       -> Owner (multiple allowed)
    start: YYYY-MM-DD, due: YYYY-MM-DD
    deps: MVP-001|MVP-002 (or comma-separated)
    deliver: free text
    note: free text

Once you’ve generated the CSV, open it in Excel/LibreOffice, or commit it to your repo.
