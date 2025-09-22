# Git Update Instructions

This project currently has no Git repository in the workspace. To publish your local changes to GitHub, follow these steps.

1. Initialize & commit locally (script provided):

```bash
# make script executable once
chmod +x scripts/git_sync.sh
# run the script (it will initialize git if needed and commit changes)
./scripts/git_sync.sh "chore: sync local docs and PERSONAS"
```

2. Create a remote repository on GitHub (via the web UI) and copy the HTTPS remote URL.

3. Add the remote and push:

```bash
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
```

4. Optional: if you prefer a branch-based PR flow, create and push a feature branch first:

```bash
git checkout -b feature/docs-personas
git push -u origin feature/docs-personas
# create a PR on GitHub from this branch
```

Security note: Do not commit secrets or credentials. Use a CI secrets store for deployment credentials.
