"""Compatibility shim for 'import app'.

Redirects this namespace to the real implementation under backend/app without
eager-importing submodules (avoids side effects during test collection).
"""

import os, sys

_here = os.path.dirname(__file__)
_candidate = os.path.abspath(os.path.join(_here, "backend", "app"))
if not os.path.isdir(_candidate):
    _candidate = os.path.abspath(os.path.join(_here, "..", "backend", "app"))

__path__ = [_candidate]

parent = os.path.dirname(_candidate)
if parent not in sys.path:
    sys.path.insert(0, parent)
