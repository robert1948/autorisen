# Ensure backend package is importable as 'app' during test collection
import sys
import os

root = os.path.dirname(__file__)
backend_path = os.path.join(root, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Add backend/app for legacy absolute imports like 'services', 'models'
backend_app_path = os.path.join(backend_path, "app")
if backend_app_path not in sys.path:
    sys.path.insert(0, backend_app_path)

print("[conftest] sys.path configured. First 5 entries:")
for p in sys.path[:5]:
    print("   ", p)
