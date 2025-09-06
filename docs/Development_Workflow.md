# Development Workflow & Checklist

This workflow ensures consistent progress on the MVP by referencing active tasks, keeping documentation updated, and maintaining project state.

---

## 1. Reference Active Tasks

- [ ] Open `docs/Checklist_MVP.md`.
- [ ] Identify the next uncompleted task or subtask.
- [ ] Confirm priority and dependencies before starting.

---

## 2. Implement the Task

- [ ] Switch to a feature branch or dedicated workspace.
- [ ] Write, test, and validate code or configuration changes.
- [ ] Run local checks (linting, unit tests, docker-compose up).

---

## 3. Update `Checklist_MVP.md`

- [ ] Mark the task as **In Progress** while working.
- [ ] After completing, mark the task as **Done** (`[x]`).
- [ ] Add a brief **Deliverables/Notes** entry under the task (e.g., files changed, feature confirmed).

---

## 4. Update `DEVELOPMENT_CONTEXT.md`

- [ ] Add/update relevant sections to reflect:
  - New features implemented.
  - Architecture or workflow changes.
  - Known issues resolved or discovered.
- [ ] Increment the version number/tag if applicable.

---

## 5. Commit & Push

- [ ] Stage both updated files:

  ```bash
  git add docs/Checklist_MVP.md docs/DEVELOPMENT_CONTEXT.md

### Dev Log Automation

Add a log entry for meaningful changes:

```bash
make devlog TYPE=feature SCOPE=agents SUMMARY="faq endpoint" IMPACT=api PR=45
```

Enable the pre-commit hook reminder:

```bash
git config core.hooksPath .githooks
```

CI job `devlog-verify` ensures required entries exist on main pushes.
