import os

# Search for the directory containing utils.py within the project root
project_root = "/workspaces/autoagent"
utils_dirs = []

for root, dirs, files in os.walk(project_root):
    if "venv" in root:
        continue  # ❌ Skip virtualenv
    if "auth_guard.py" in files:
        utils_dirs.append(root)

print(utils_dirs)
