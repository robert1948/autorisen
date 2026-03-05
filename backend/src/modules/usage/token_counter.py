"""Accurate token counting with graceful fallback.

Uses ``tiktoken`` when available for precise token counts, falling back
to the 4-chars-per-token heuristic when the library is not installed.

Usage::

    from backend.src.modules.usage.token_counter import count_tokens

    n = count_tokens("Hello, how are you?")            # → 6 (exact)
    n = count_tokens(text, model="claude-3-5-haiku")   # → uses cl100k_base
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

# ── Heuristic fallback ────────────────────────────────────────────────────────
_CHARS_PER_TOKEN = 4

# ── tiktoken setup ────────────────────────────────────────────────────────────
_encoder = None
_tiktoken_available = False

try:
    import tiktoken

    # cl100k_base covers GPT-4, GPT-3.5-turbo, and is a reasonable
    # approximation for Claude models as well.
    _encoder = tiktoken.get_encoding("cl100k_base")
    _tiktoken_available = True
    log.debug("tiktoken loaded — using cl100k_base encoding for token counting")
except ImportError:
    log.info(
        "tiktoken not installed — falling back to %d-chars-per-token heuristic. "
        "Install with: pip install tiktoken",
        _CHARS_PER_TOKEN,
    )
except Exception:
    log.warning("tiktoken failed to initialise", exc_info=True)


def count_tokens(text: str, *, model: str | None = None) -> int:
    """Count the number of tokens in *text*.

    Parameters
    ----------
    text:
        The text to tokenise.
    model:
        Optional model name (currently ignored — all models use cl100k_base).
        Reserved for future per-model encoding selection.

    Returns
    -------
    int
        Token count (minimum 1 for non-empty text).
    """
    if not text:
        return 0

    if _tiktoken_available and _encoder is not None:
        return len(_encoder.encode(text))

    # Heuristic fallback
    return max(1, len(text) // _CHARS_PER_TOKEN)


def is_exact() -> bool:
    """Return True if tiktoken is available for exact counting."""
    return _tiktoken_available
