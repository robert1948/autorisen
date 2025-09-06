# Proxy to backend.app.utils
import sys, os

_backend_utils = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "backend", "app", "utils"
)
if _backend_utils not in sys.path:
    sys.path.insert(0, _backend_utils)
from datetime import datetime  # noqa: F401
