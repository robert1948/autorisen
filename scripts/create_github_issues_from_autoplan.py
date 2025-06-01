import os
from github import Github
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Load GitHub token and repo
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPO", "robert1948/autoagent")
AUTOPLAN_FILE = "Autoplan.md"

if not GITHUB_TOKEN:
    raise ValueError("Missing GITHUB_TOKEN in environment.")

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Define the milestone title
milestone_title = "Milestone 4: Autoplan Tasks"
milestone_description = "Auto-generated from Autoplan.md unchecked items."
milestone_due_date = datetime.now().replace(hour=23, minute=59, second=59)

# Get or create the milestone
milestone = None
for m in repo.get_milestones(state="open"):
    if m.title == milestone_title:
        milestone = m
        break

if not milestone:
    milestone = repo.create_milestone(
        title=milestone_title,
        state="open",
        description=milestone_description,
        due_on=milestone_due_date
    )

# Parse tasks from Autoplan.md


def extract_unchecked_tasks(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()
    return [line.strip()[5:] for line in lines if line.strip().startswith("- [ ] ")]


unchecked_tasks = extract_unchecked_tasks(AUTOPLAN_FILE)

# Get existing issue titles to avoid duplicates
existing_titles = [issue.title for issue in repo.get_issues(state="all")]

# Create issues for each unchecked task
created = 0
for task in unchecked_tasks:
    if task not in existing_titles:
        repo.create_issue(
            title=task,
            body=f"Auto-created from `{AUTOPLAN_FILE}`.\n\n> Task: `{task}`",
            milestone=milestone
        )
        created += 1

print(f"✅ Created {created} new issues from Autoplan.md.")
