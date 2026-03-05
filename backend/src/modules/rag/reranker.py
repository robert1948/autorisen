"""Lightweight re-ranking for RAG retrieval candidates.

After the initial cosine-similarity retrieval, re-rank the top-K
candidates using keyword overlap (BM25-inspired) scoring.  This is a
*zero-cost* re-ranker — no LLM call or external API required — that
improves precision by promoting chunks whose surface tokens best match
the query.

Usage::

    from backend.src.modules.rag.reranker import rerank_chunks

    reranked = rerank_chunks(query, candidates, top_n=5)
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any, List, Sequence, Tuple

# BM25 tuning constants
_K1 = 1.2   # term-frequency saturation
_B = 0.75   # length normalisation

# Word tokeniser — split on non-alphanumeric runs
_WORD_RE = re.compile(r"[a-zA-Z0-9]+")


def _tokenise(text: str) -> List[str]:
    """Lowercase word tokenisation."""
    return _WORD_RE.findall(text.lower())


def _bm25_score(
    query_tokens: List[str],
    doc_tokens: List[str],
    avg_dl: float,
    df: dict[str, int],
    n_docs: int,
) -> float:
    """Compute BM25 relevance score for a single document."""
    tf = Counter(doc_tokens)
    dl = len(doc_tokens)
    score = 0.0
    for qt in query_tokens:
        if qt not in tf:
            continue
        # IDF component (with smoothing to avoid negative values)
        idf = math.log((n_docs - df.get(qt, 0) + 0.5) / (df.get(qt, 0) + 0.5) + 1.0)
        # TF component with saturation
        numerator = tf[qt] * (_K1 + 1)
        denominator = tf[qt] + _K1 * (1 - _B + _B * dl / max(avg_dl, 1))
        score += idf * (numerator / denominator)
    return score


def rerank_chunks(
    query: str,
    candidates: Sequence[Tuple[Any, float, Any]],
    *,
    top_n: int | None = None,
    embedding_weight: float = 0.4,
    bm25_weight: float = 0.6,
) -> List[Tuple[Any, float, Any]]:
    """Re-rank retrieval candidates using a hybrid cosine + BM25 score.

    Parameters
    ----------
    query:
        The user query string.
    candidates:
        A sequence of ``(chunk, cosine_score, document)`` tuples as
        returned by ``_retrieve_chunks``.
    top_n:
        Maximum results to return.  ``None`` keeps all.
    embedding_weight:
        Weight for the normalised cosine similarity score (0-1).
    bm25_weight:
        Weight for the normalised BM25 keyword score (0-1).

    Returns
    -------
    list
        Re-ranked ``(chunk, hybrid_score, document)`` tuples.
    """
    if not candidates:
        return list(candidates)

    query_tokens = _tokenise(query)
    if not query_tokens:
        return list(candidates)

    # Tokenise all chunk texts
    doc_token_lists = []
    for chunk, _score, _doc in candidates:
        text = getattr(chunk, "text", "") or ""
        doc_token_lists.append(_tokenise(text))

    # Compute document frequency for IDF
    n_docs = len(doc_token_lists)
    df: dict[str, int] = {}
    for tokens in doc_token_lists:
        for t in set(tokens):
            df[t] = df.get(t, 0) + 1

    avg_dl = sum(len(t) for t in doc_token_lists) / max(n_docs, 1)

    # Score each candidate
    scored: List[Tuple[Any, float, Any, float, float]] = []
    for (chunk, cos_score, doc), dtokens in zip(candidates, doc_token_lists):
        bm = _bm25_score(query_tokens, dtokens, avg_dl, df, n_docs)
        scored.append((chunk, cos_score, doc, cos_score, bm))

    # Normalise scores to [0, 1] for fair blending
    max_cos = max(s[3] for s in scored) or 1.0
    max_bm = max(s[4] for s in scored) or 1.0

    hybrid: List[Tuple[Any, float, Any]] = []
    for chunk, _old_score, doc, cs, bm in scored:
        norm_cs = cs / max_cos
        norm_bm = bm / max_bm if max_bm > 0 else 0.0
        h = embedding_weight * norm_cs + bm25_weight * norm_bm
        hybrid.append((chunk, round(h, 6), doc))

    hybrid.sort(key=lambda x: x[1], reverse=True)

    if top_n is not None:
        hybrid = hybrid[:top_n]

    return hybrid
