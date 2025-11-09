from fastapi import APIRouter

from .._shim_utils import _first_ok

try:
    router = _first_ok([
        lambda: __import__("backend.src.modules.voice.router", fromlist=["router"]).router,
        lambda: __import__("backend.src.modules.voice", fromlist=["router"]).router,
    ])
except ImportError:
    router = APIRouter()
