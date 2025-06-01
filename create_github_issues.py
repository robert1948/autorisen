from github import Github

# --- SETUP ---
import os
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # ✅ SECURE
REPO_NAME = "robert1948/autoagent"

# --- Connect to GitHub ---
g = Github(ACCESS_TOKEN)
repo = g.get_repo(REPO_NAME)

# --- Create Milestone ---
milestone = repo.create_milestone(
    title="Milestone 1 – Public MVP",
    state="open",
    description="Track key tasks required to complete and launch the first public-facing MVP of Autorisen."
)

# --- Issues to Create ---
tasks = [
    "Finalize frontend login and register pages with Bootstrap styling",
    "Deploy updated backend with /me endpoint support to Heroku",
    "Serve React frontend correctly from FastAPI static path",
    "Test all major flows on localhost before production",
    "Document deployment process and configs in README"
]

# --- Create Issues Linked to Milestone ---
for task in tasks:
    repo.create_issue(title=task, milestone=milestone)

print("✅ Milestone and issues created successfully.")
