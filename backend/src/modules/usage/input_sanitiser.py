"""Pre-LLM input sanitisation — strip noise, redact PII, compress whitespace.

Applied before ``validate_llm_input()`` to reduce token waste from
HTML tags, email signatures, excessive whitespace, and common boilerplate.

Also provides lightweight PII redaction to avoid sending personally
identifiable information to LLM providers (POPIA/GDPR compliance).

Usage::

    from backend.src.modules.usage.input_sanitiser import sanitise_input

    clean = sanitise_input(raw_text)
"""

from __future__ import annotations

import re

# ── HTML / Markdown noise ─────────────────────────────────────────────────────

# Strip HTML tags (but preserve the text content).
_HTML_TAG_RE = re.compile(r"<[^>]+>")

# Collapse runs of 3+ newlines into 2.
_EXCESSIVE_NEWLINES_RE = re.compile(r"\n{3,}")

# Collapse runs of 3+ spaces into 1.
_EXCESSIVE_SPACES_RE = re.compile(r"[ \t]{3,}")

# ── Email signature patterns ──────────────────────────────────────────────────

_SIGNATURE_MARKERS = [
    re.compile(r"^--\s*$", re.MULTILINE),             # Classic -- marker
    re.compile(r"^Sent from my (iPhone|iPad|Android|Galaxy)", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^Get Outlook for", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^_{10,}", re.MULTILINE),              # __________ divider
    re.compile(r"^-{10,}", re.MULTILINE),              # ---------- divider
]

# ── PII patterns (conservative — only obvious patterns) ──────────────────────

# South African ID numbers (13 digits starting with date-of-birth pattern)
_SA_ID_RE = re.compile(r"\b(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{7})\b")

# Credit card numbers (13-19 digits with optional separators)
_CREDIT_CARD_RE = re.compile(
    r"\b(?:\d[ -]*?){13,19}\b"
)

# Email addresses (redact to preserve context without leaking PII)
_EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
)

# Phone numbers (South African + international formats)
_PHONE_RE = re.compile(
    r"\b(?:\+?27|0)[\s-]?\d{2}[\s-]?\d{3}[\s-]?\d{4}\b"
    r"|\b\+?\d{1,3}[\s-]?\(?\d{2,3}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}\b"
)


def strip_html(text: str) -> str:
    """Remove HTML tags, preserving text content."""
    return _HTML_TAG_RE.sub("", text)


def compress_whitespace(text: str) -> str:
    """Collapse excessive whitespace and blank lines."""
    text = _EXCESSIVE_SPACES_RE.sub(" ", text)
    text = _EXCESSIVE_NEWLINES_RE.sub("\n\n", text)
    return text.strip()


def strip_email_signature(text: str) -> str:
    """Remove common email signature blocks."""
    for pattern in _SIGNATURE_MARKERS:
        match = pattern.search(text)
        if match:
            # Keep everything before the signature marker
            text = text[: match.start()].rstrip()
            break
    return text


def redact_pii(text: str) -> str:
    """Replace obvious PII patterns with redaction tokens.

    This is a lightweight, conservative redaction layer — it catches
    obvious patterns (IDs, credit cards, emails, phone numbers) but
    does not attempt deep NER. Useful as a first line of defence.
    """
    text = _SA_ID_RE.sub("[REDACTED_ID]", text)
    text = _CREDIT_CARD_RE.sub("[REDACTED_CARD]", text)
    text = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = _PHONE_RE.sub("[REDACTED_PHONE]", text)
    return text


def sanitise_input(
    text: str,
    *,
    strip_signatures: bool = True,
    redact: bool = True,
) -> str:
    """Full pre-processing pipeline before LLM input.

    Parameters
    ----------
    text:
        Raw user input.
    strip_signatures:
        Remove email signature blocks.
    redact:
        Apply PII redaction.

    Returns
    -------
    str
        Cleaned text ready for ``validate_llm_input()``.
    """
    if not text:
        return text

    text = strip_html(text)

    if strip_signatures:
        text = strip_email_signature(text)

    text = compress_whitespace(text)

    if redact:
        text = redact_pii(text)

    return text
