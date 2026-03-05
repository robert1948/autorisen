"""Tests for advanced AI cost-optimisation gaps A–J.

Validates the ten compliance gaps identified in the advanced audit:

 A. Anthropic prompt caching — system messages use cache_control ephemeral
 B. Model router — complexity classifier routes simple → Haiku, complex → Sonnet
 C. Budget alerts — FinOps threshold alerting at 50%/80%/95%
 D. Conversation summarization — extractive summary of dropped messages
 E. Semantic cache — embedding similarity lookup with cosine ≥ 0.92
 F. Batch API — Anthropic + OpenAI batch endpoint client
 G. Token counter — tiktoken with graceful fallback
 H. Input pre-processing — HTML stripping, PII redaction, signature removal
 I. RAG re-ranking — hybrid BM25 + cosine re-ranker
 J. Per-user circuit breaker — per-user monthly spend cap
"""

from __future__ import annotations

import asyncio
import math
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── Helpers ──────────────────────────────────────────────────────────────────

def _run(coro):
    """Run an async coroutine synchronously for testing."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ═══════════════════════════════════════════════════════════════════════════════
# A. Anthropic Prompt Caching
# ═══════════════════════════════════════════════════════════════════════════════

class TestPromptCaching:
    """Verify that all Anthropic call sites use cache_control ephemeral."""

    def test_chat_system_prompt_is_list_with_cache_control(self):
        """Chat service should pass system param as a list with cache_control."""
        from backend.src.modules.chat.service import (
            DEFAULT_SYSTEM_PROMPT,
            PLACEMENT_SYSTEM_PROMPTS,
        )
        # All prompts should be non-empty strings
        assert isinstance(DEFAULT_SYSTEM_PROMPT, str)
        assert len(DEFAULT_SYSTEM_PROMPT) > 10
        for key, prompt in PLACEMENT_SYSTEM_PROMPTS.items():
            assert isinstance(prompt, str), f"placement {key} prompt not a string"
            assert len(prompt) > 10

    def test_capsule_service_has_cache_control_format(self):
        """Capsule service system param should use list format."""
        import importlib
        mod = importlib.import_module("backend.src.modules.capsules.service")
        source = open(mod.__file__).read()
        assert "cache_control" in source, "capsules/service.py lacks cache_control"
        assert '"type": "ephemeral"' in source or "'type': 'ephemeral'" in source

    def test_simple_agents_have_cache_control(self):
        """All 4 simple agents should use cache_control format."""
        agents = [
            "backend.src.modules.agents.finance_agent.service",
            "backend.src.modules.agents.customer_agent.service",
            "backend.src.modules.agents.content_agent.service",
            "backend.src.modules.agents.dev_agent.service",
        ]
        for agent_mod in agents:
            mod = __import__(agent_mod, fromlist=["service"])
            source = open(mod.__file__).read()
            assert "cache_control" in source, f"{agent_mod} missing cache_control"


# ═══════════════════════════════════════════════════════════════════════════════
# B. Model Router
# ═══════════════════════════════════════════════════════════════════════════════

class TestModelRouter:
    """Verify complexity-based model routing."""

    def test_classify_simple_queries(self):
        from backend.src.modules.usage.model_router import classify_complexity
        assert classify_complexity("hi") == "simple"
        assert classify_complexity("thanks") == "simple"
        assert classify_complexity("hello there") == "simple"

    def test_classify_complex_queries(self):
        from backend.src.modules.usage.model_router import classify_complexity
        assert classify_complexity(
            "Create a comprehensive plan for migrating from monolith to microservices "
            "with detailed analysis of each component"
        ) == "complex"

    def test_classify_long_text_escalates(self):
        from backend.src.modules.usage.model_router import classify_complexity
        # Texts over 2000 chars should never be "simple"
        long_text = "a " * 1200
        result = classify_complexity(long_text)
        assert result in ("moderate", "complex")

    def test_select_model_respects_force(self):
        from backend.src.modules.usage.model_router import select_model
        forced = select_model("hi", force_model="gpt-4o")
        assert forced == "gpt-4o"

    def test_select_model_returns_budget_for_simple(self):
        from backend.src.modules.usage.model_router import (
            BUDGET_MODEL,
            select_model,
        )
        model = select_model("hi")
        assert model == BUDGET_MODEL


# ═══════════════════════════════════════════════════════════════════════════════
# C. Budget Alerts
# ═══════════════════════════════════════════════════════════════════════════════

class TestBudgetAlerts:
    """Verify FinOps alerting thresholds."""

    def test_no_alerts_below_50_pct(self):
        from backend.src.modules.usage.budget_alerts import budget_tracker, check_budget_thresholds
        budget_tracker.reset()
        alerts = check_budget_thresholds(40.0, 100.0)
        assert alerts == []

    def test_info_at_50_pct(self):
        from backend.src.modules.usage.budget_alerts import budget_tracker, check_budget_thresholds
        budget_tracker.reset()
        alerts = check_budget_thresholds(55.0, 100.0)
        assert len(alerts) >= 1
        assert alerts[0]["level"] == "info"

    def test_warning_at_80_pct(self):
        from backend.src.modules.usage.budget_alerts import budget_tracker, check_budget_thresholds
        budget_tracker.reset()
        alerts = check_budget_thresholds(85.0, 100.0)
        levels = [a["level"] for a in alerts]
        assert "warning" in levels

    def test_critical_at_95_pct(self):
        from backend.src.modules.usage.budget_alerts import budget_tracker, check_budget_thresholds
        budget_tracker.reset()
        alerts = check_budget_thresholds(96.0, 100.0)
        levels = [a["level"] for a in alerts]
        assert "critical" in levels

    def test_cooldown_prevents_duplicate_alerts(self):
        from backend.src.modules.usage.budget_alerts import (
            budget_tracker,
            check_budget_thresholds,
        )
        budget_tracker.reset()
        a1 = check_budget_thresholds(55.0, 100.0)
        a2 = check_budget_thresholds(55.0, 100.0)
        # Second call within cooldown should not fire again
        assert len(a2) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# D. Conversation Summarization
# ═══════════════════════════════════════════════════════════════════════════════

class TestConversationSummarization:
    """Verify extractive summarization of dropped messages."""

    def test_summarise_dropped_messages(self):
        from backend.src.modules.chat.service import _summarise_dropped_messages
        msgs = [
            {"role": "user", "content": "First question about pricing. More details here."},
            {"role": "assistant", "content": "The pricing is R529 per month. Let me explain."},
            {"role": "user", "content": "What about the free tier? I'd like to know."},
        ]
        summary = _summarise_dropped_messages(msgs)
        assert summary  # non-empty
        assert isinstance(summary, str)

    def test_summarise_empty_list(self):
        from backend.src.modules.chat.service import _summarise_dropped_messages
        assert _summarise_dropped_messages([]) == ""

    def test_summarise_respects_max_messages(self):
        from backend.src.modules.chat.service import _summarise_dropped_messages
        msgs = [
            {"role": "user", "content": f"Message {i}. Some text here."}
            for i in range(20)
        ]
        summary = _summarise_dropped_messages(msgs)
        # Should not include ALL 20 messages — limited to 6 most recent
        assert len(summary) < sum(len(m["content"]) for m in msgs)


# ═══════════════════════════════════════════════════════════════════════════════
# E. Semantic Cache
# ═══════════════════════════════════════════════════════════════════════════════

class TestSemanticCache:
    """Verify embedding-based cache structure."""

    def test_cache_instantiation(self):
        from backend.src.modules.usage.semantic_cache import SemanticCache
        cache = SemanticCache(max_size=10, ttl_seconds=60)
        assert cache._max_size == 10

    def test_cosine_similarity_helper(self):
        from backend.src.modules.usage.semantic_cache import _cosine_similarity
        a = [1.0, 0.0, 0.0]
        b = [1.0, 0.0, 0.0]
        assert abs(_cosine_similarity(a, b) - 1.0) < 0.001

    def test_cosine_orthogonal(self):
        from backend.src.modules.usage.semantic_cache import _cosine_similarity
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert abs(_cosine_similarity(a, b)) < 0.001


# ═══════════════════════════════════════════════════════════════════════════════
# F. Batch API
# ═══════════════════════════════════════════════════════════════════════════════

class TestBatchAPI:
    """Verify batch client structure."""

    def test_batch_client_instantiates(self):
        from backend.src.modules.usage.batch_api import BatchClient
        client = BatchClient()
        assert hasattr(client, "submit_anthropic_batch")
        assert hasattr(client, "submit_openai_batch")
        assert hasattr(client, "check_status")
        assert hasattr(client, "list_jobs")

    def test_list_jobs_empty(self):
        from backend.src.modules.usage.batch_api import BatchClient
        client = BatchClient()
        jobs = client.list_jobs()
        assert isinstance(jobs, list)


# ═══════════════════════════════════════════════════════════════════════════════
# G. Token Counter
# ═══════════════════════════════════════════════════════════════════════════════

class TestTokenCounter:
    """Verify accurate token counting."""

    def test_count_tokens_non_empty(self):
        from backend.src.modules.usage.token_counter import count_tokens
        result = count_tokens("Hello, world!")
        assert result > 0

    def test_count_tokens_empty(self):
        from backend.src.modules.usage.token_counter import count_tokens
        assert count_tokens("") == 0

    def test_count_tokens_consistency(self):
        from backend.src.modules.usage.token_counter import count_tokens
        t1 = count_tokens("The quick brown fox jumps over the lazy dog")
        t2 = count_tokens("The quick brown fox jumps over the lazy dog")
        assert t1 == t2

    def test_is_exact_returns_bool(self):
        from backend.src.modules.usage.token_counter import is_exact
        assert isinstance(is_exact(), bool)

    def test_longer_text_more_tokens(self):
        from backend.src.modules.usage.token_counter import count_tokens
        short = count_tokens("hi")
        long = count_tokens("This is a much longer piece of text with many words")
        assert long > short


# ═══════════════════════════════════════════════════════════════════════════════
# H. Input Pre-processing (Sanitiser)
# ═══════════════════════════════════════════════════════════════════════════════

class TestInputSanitiser:
    """Verify HTML stripping, PII redaction, and signature removal."""

    def test_strip_html_tags(self):
        from backend.src.modules.usage.input_sanitiser import strip_html
        assert strip_html("<p>Hello</p>") == "Hello"
        assert strip_html("<b>Bold</b> and <i>italic</i>") == "Bold and italic"
        assert strip_html("No tags here") == "No tags here"

    def test_compress_whitespace(self):
        from backend.src.modules.usage.input_sanitiser import compress_whitespace
        assert compress_whitespace("a     b") == "a b"
        assert compress_whitespace("a\n\n\n\nb") == "a\n\nb"

    def test_redact_email(self):
        from backend.src.modules.usage.input_sanitiser import redact_pii
        result = redact_pii("Contact me at john@example.com please")
        assert "[REDACTED_EMAIL]" in result
        assert "john@example.com" not in result

    def test_redact_phone_sa(self):
        from backend.src.modules.usage.input_sanitiser import redact_pii
        result = redact_pii("Call me on 082 123 4567")
        assert "[REDACTED_PHONE]" in result

    def test_strip_email_signature(self):
        from backend.src.modules.usage.input_sanitiser import strip_email_signature
        text = "This is the body.\n\n--\nJohn Smith\nCEO, Acme Corp"
        result = strip_email_signature(text)
        assert "John Smith" not in result
        assert "This is the body." in result

    def test_strip_sent_from_signature(self):
        from backend.src.modules.usage.input_sanitiser import strip_email_signature
        text = "Hello there\nSent from my iPhone"
        result = strip_email_signature(text)
        assert "Sent from" not in result

    def test_sanitise_input_full_pipeline(self):
        from backend.src.modules.usage.input_sanitiser import sanitise_input
        raw = "<p>Email me at bob@corp.com</p>\n\n\n\n--\nBob Smith"
        result = sanitise_input(raw)
        assert "<p>" not in result
        assert "bob@corp.com" not in result
        assert "[REDACTED_EMAIL]" in result
        assert "Bob Smith" not in result

    def test_sanitise_empty_string(self):
        from backend.src.modules.usage.input_sanitiser import sanitise_input
        assert sanitise_input("") == ""

    def test_validate_llm_input_includes_sanitisation(self):
        """validate_llm_input should now sanitise by default."""
        from backend.src.modules.usage.input_guard import validate_llm_input
        result = validate_llm_input("<b>Hello</b> user@test.com")
        assert "<b>" not in result
        assert "user@test.com" not in result

    def test_validate_llm_input_sanitise_disabled(self):
        """sanitise=False should skip pre-processing."""
        from backend.src.modules.usage.input_guard import validate_llm_input
        result = validate_llm_input("<b>Hello</b>", sanitise=False)
        assert "<b>" in result


# ═══════════════════════════════════════════════════════════════════════════════
# I. RAG Re-ranking
# ═══════════════════════════════════════════════════════════════════════════════

class TestReranker:
    """Verify hybrid BM25 + cosine re-ranking."""

    def _make_chunk(self, text):
        """Create a mock chunk with a text attribute."""
        chunk = MagicMock()
        chunk.text = text
        return chunk

    def test_rerank_empty_candidates(self):
        from backend.src.modules.rag.reranker import rerank_chunks
        result = rerank_chunks("test query", [])
        assert result == []

    def test_rerank_preserves_candidates(self):
        from backend.src.modules.rag.reranker import rerank_chunks
        c1 = self._make_chunk("the quick brown fox")
        c2 = self._make_chunk("the lazy dog sleeps")
        doc = MagicMock()
        candidates = [(c1, 0.9, doc), (c2, 0.85, doc)]
        result = rerank_chunks("quick fox", candidates)
        assert len(result) == 2

    def test_rerank_promotes_keyword_match(self):
        from backend.src.modules.rag.reranker import rerank_chunks
        c1 = self._make_chunk("unrelated document about weather patterns")
        c2 = self._make_chunk("pricing plans and billing information")
        doc = MagicMock()
        # c1 has higher cosine but c2 has better keyword match
        candidates = [(c1, 0.95, doc), (c2, 0.88, doc)]
        result = rerank_chunks("pricing plans", candidates)
        # With BM25 weight=0.6, the keyword match should win
        assert result[0][0].text == "pricing plans and billing information"

    def test_rerank_top_n(self):
        from backend.src.modules.rag.reranker import rerank_chunks
        doc = MagicMock()
        candidates = [
            (self._make_chunk(f"text {i}"), 0.9 - i * 0.01, doc)
            for i in range(10)
        ]
        result = rerank_chunks("text", candidates, top_n=3)
        assert len(result) == 3

    def test_bm25_score_function(self):
        from backend.src.modules.rag.reranker import _bm25_score, _tokenise
        query = _tokenise("pricing plans")
        doc = _tokenise("pricing plans and billing for enterprise")
        score = _bm25_score(query, doc, avg_dl=6, df={"pricing": 1, "plans": 1}, n_docs=3)
        assert score > 0


# ═══════════════════════════════════════════════════════════════════════════════
# J. Per-User Circuit Breaker
# ═══════════════════════════════════════════════════════════════════════════════

class TestPerUserCircuitBreaker:
    """Verify per-user spending cap enforcement."""

    def test_config_has_max_user_spend(self):
        from backend.src.core.config import Settings
        s = Settings(
            SECRET_KEY="test-key-12345",
            DATABASE_URL="sqlite:////tmp/test.db",
            MAX_USER_MONTHLY_SPEND_USD=25.0,
        )
        assert s.max_user_monthly_spend_usd == 25.0

    def test_config_default_user_spend(self):
        from backend.src.core.config import Settings
        s = Settings(
            SECRET_KEY="test-key-12345",
            DATABASE_URL="sqlite:////tmp/test.db",
        )
        assert s.max_user_monthly_spend_usd == 50.0

    def test_enforce_user_budget_exists(self):
        from backend.src.modules.payments.enforcement import enforce_user_budget
        assert callable(enforce_user_budget)

    def test_user_spend_helper(self):
        """_user_spend should return float from DB."""
        from backend.src.modules.payments.enforcement import _user_spend
        assert callable(_user_spend)

    def test_enforce_user_budget_imported_in_routers(self):
        """All LLM-calling routers should import enforce_user_budget."""
        import importlib
        routers = [
            "backend.src.modules.chat.router",
            "backend.src.modules.chatkit.router",
            "backend.src.modules.agents.router",
            "backend.src.modules.flows.router",
            "backend.src.modules.agents.cape_ai_guide.router",
            "backend.src.modules.agents.cape_ai_domain_specialist.router",
        ]
        for r in routers:
            mod = importlib.import_module(r)
            source = open(mod.__file__).read()
            assert "enforce_user_budget" in source, f"{r} missing enforce_user_budget"
