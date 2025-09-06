"""Namespace shim for legacy 'services.*' imports in tests.

Resolves to backend/app/services modules.
"""

import sys, os


_pkg_dir = os.path.dirname(__file__)
_candidate = os.path.abspath(os.path.join(_pkg_dir, "..", "backend", "app", "services"))
if not os.path.isdir(_candidate):
    raise ImportError(
        f"Cannot locate backend/app/services at expected path: {_candidate}"
    )

# Expose real services directory as this package's path
__path__ = [_candidate]
