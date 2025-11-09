from fastapi import FastAPI

from ._shim_utils import _first_ok

try:
    # Your real app
    app = _first_ok([
        lambda: __import__("backend.src.app", fromlist=["app"]).app,
        lambda: __import__("backend.app", fromlist=["app"]).app,            # alt layout
    ])
except ImportError:
    # Minimal fallback to avoid import errors during collection
    app = FastAPI(title="Shim fallback (app.main)")
