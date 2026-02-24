"""RAG module — Embedding generation and document chunking."""

from __future__ import annotations

import hashlib
import logging
import math
import re
from typing import List, Optional, Tuple

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

# Target ~400 tokens per chunk  (~1600 chars for English text)
DEFAULT_CHUNK_SIZE = 1600
DEFAULT_CHUNK_OVERLAP = 200


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """Split text into overlapping chunks, preferring paragraph/sentence boundaries.

    Returns a list of non-empty chunk strings.
    """
    if not text or not text.strip():
        return []

    # Normalise whitespace
    text = re.sub(r"\r\n", "\n", text)

    # Try to split on paragraphs first
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if not paragraphs:
        return [text.strip()]

    chunks: List[str] = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # If a single paragraph exceeds chunk_size, split by sentences
            if len(para) > chunk_size:
                sentences = re.split(r"(?<=[.!?])\s+", para)
                buf = ""
                for sent in sentences:
                    test = f"{buf} {sent}".strip() if buf else sent
                    if len(test) <= chunk_size:
                        buf = test
                    else:
                        if buf:
                            chunks.append(buf)
                        buf = sent
                current = buf
            else:
                current = para

    if current:
        chunks.append(current)

    # Apply overlap: prepend tail of previous chunk to each subsequent chunk
    if overlap > 0 and len(chunks) > 1:
        overlapped: List[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            tail = chunks[i - 1][-overlap:]
            overlapped.append(f"{tail} {chunks[i]}".strip())
        chunks = overlapped

    return chunks


# ---------------------------------------------------------------------------
# Embedding via OpenAI
# ---------------------------------------------------------------------------

_EMBEDDING_MODEL = "text-embedding-3-small"
_EMBEDDING_DIM = 1536


async def generate_embeddings(
    texts: List[str],
    api_key: Optional[str] = None,
) -> List[List[float]]:
    """Generate embeddings for a list of texts using OpenAI.

    Falls back to a deterministic hash-based pseudo-embedding when no API key
    is available (development / testing only).
    """
    if not texts:
        return []

    if api_key:
        return await _openai_embeddings(texts, api_key)

    log.warning("No OpenAI API key — using hash-based pseudo-embeddings (dev only)")
    return [_hash_embedding(t) for t in texts]


async def _openai_embeddings(texts: List[str], api_key: str) -> List[List[float]]:
    """Call OpenAI embeddings API in batches."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key)
    all_embeddings: List[List[float]] = []

    # OpenAI supports up to 2048 inputs per request; batch at 100 for safety
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = await client.embeddings.create(
            model=_EMBEDDING_MODEL,
            input=batch,
        )
        for item in resp.data:
            all_embeddings.append(item.embedding)

    return all_embeddings


def _hash_embedding(text: str, dim: int = _EMBEDDING_DIM) -> List[float]:
    """Deterministic pseudo-embedding from SHA-256 — for dev/test only.

    Produces a unit-length vector so cosine similarity still works directionally.
    """
    digest = hashlib.sha256(text.encode()).hexdigest()
    raw = [int(digest[i : i + 2], 16) / 255.0 for i in range(0, min(len(digest), dim * 2), 2)]
    # Pad or tile to target dimension
    while len(raw) < dim:
        raw = raw + raw
    raw = raw[:dim]
    # Normalise to unit length
    magnitude = math.sqrt(sum(x * x for x in raw))
    if magnitude > 0:
        raw = [x / magnitude for x in raw]
    return raw


def embedding_dimensions() -> int:
    """Return the dimensionality used by the current embedding model."""
    return _EMBEDDING_DIM


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)
