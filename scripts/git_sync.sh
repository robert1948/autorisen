#!/usr/bin/env bash
# Helper script to initialize a git repo (if needed), commit all changes, and show push commands.
# This script DOES NOT add a remote or push automatically because that requires credentials and
# a repository URL from the user. Run this script locally and then follow the printed instructions.

set -euo pipefail

COMMIT_MSG=${1:-"chore: sync local docs and persona updates"}

ROOT_DIR="$(pwd)"

if [ ! -d "$ROOT_DIR/.git" ]; then
  echo "No .git found in $ROOT_DIR — initializing a new git repository..."
  git init -b main
  echo "Created git repo and default branch 'main'."
else
  echo "Git repository detected in $ROOT_DIR"
fi

# Add sensible .gitignore if missing
if [ ! -f ".gitignore" ]; then
  cat > .gitignore <<'EOF'
# Python
__pycache__/
*.py[cod]

# Node
node_modules/

# Editor
.vscode/
.idea/
*~

# OS
.DS_Store
EOF
  echo "Created .gitignore"
fi

# Stage all files
git add -A

# Commit (allow empty commits to record intent)
if git diff --cached --quiet; then
  echo "No staged changes to commit. Skipping commit."
else
  git commit -m "$COMMIT_MSG"
  echo "Committed changes with message: $COMMIT_MSG"
fi

echo
cat <<'HELP'
Next steps to push to GitHub (run these manually):

1. Create a repository on GitHub (via web UI). Copy its HTTPS remote URL (e.g. https://github.com/<owner>/<repo>.git)

2. Add the remote and push:

   git remote add origin <REMOTE_URL>
   git push -u origin main

If your remote uses 'master' as the default branch, replace 'main' with 'master'.

If you want me to create a branch and open a PR or do more remote operations, provide the remote URL and confirm you want me to proceed (I will not push without explicit permission).
HELP
