#!/bin/bash

PROJECT_NUMBER=1
OWNER="robert1948"
REPO="tailstorm"

declare -a TASKS=(
  "Build auth form components (Login/Register)"
  "Create main.jsx routing + Tailwind setup"
  "Configure Heroku deployment with Dockerfile and heroku.yml"
  "Set up PostgreSQL and backend (FastAPI or Django)"
  "Create /register, /login, /me endpoints"
)

for TASK in "${TASKS[@]}"; do
  echo "Creating issue: $TASK"
  ISSUE_URL=$(gh issue create --title "$TASK" --repo "$OWNER/$REPO" --body "Auto-generated from Checklist.md." --label "autoagent" --assignee "$OWNER" --json url --jq .url)

  echo "Adding to project..."
  gh project item-add $PROJECT_NUMBER --owner $OWNER --url "$ISSUE_URL"
done
