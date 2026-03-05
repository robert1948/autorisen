"""Pre-LLM input validation guards.

Prevents oversized or empty inputs from reaching the LLM, saving tokens
and protecting against abuse.  Import ``validate_llm_input`` and call it
before every LLM invocation.
"""

from __future__ import annotations

import logging

from backend.src.modules.usage.input_sanitiser import sanitise_input

log = logging.getLogger(__name__)

# Maximum characters allowed in a user prompt before truncation.
# ~8 000 chars ≈ ~2 000 tokens — leaves ample room for system prompt + output.
MAX_INPUT_CHARS: int = 8_000


class InputTooLong(ValueError):
    """Raised when the caller sets ``truncate=False`` and input exceeds the cap."""


def validate_llm_input(
    text: str,
    *,
    max_chars: int = MAX_INPUT_CHARS,
    truncate: bool = True,
    label: str = "input",
    sanitise: bool = True,
) -> str:
    """Validate, sanitise, and optionally truncate LLM input text.

    Parameters
    ----------
    text:
        The raw user input / prompt body.
    max_chars:
        Character ceiling (default ``MAX_INPUT_CHARS``).
    truncate:
        If ``True`` (default), silently truncate and append an ellipsis.
        If ``False``, raise ``InputTooLong``.
    label:
        Human-readable label for log messages (e.g. ``"chat message"``).
    sanitise:
        If ``True`` (default), apply HTML stripping, PII redaction,
        email signature removal, and whitespace normalisation before
        length checks.

    Returns
    -------
    str
        The sanitised and (possibly truncated) text.
    """
    text = (text or "").strip()
    if not text:
        return text

    if sanitise:
        text = sanitise_input(text)

    if len(text) > max_chars:
        if truncate:
            original_len = len(text)
            text = text[:max_chars] + "…"
            log.warning(
                "Truncated %s from %d to %d chars before LLM call",
                label,
                original_len,
                max_chars,
            )
        else:
            raise InputTooLong(
                f"{label} exceeds maximum length ({len(text)} > {max_chars} chars)"
            )
    return text
