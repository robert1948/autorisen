import sys, os

root = os.path.dirname(__file__)
backend_path = os.path.join(root, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
