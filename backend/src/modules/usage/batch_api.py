"""Batch API client — queue non-latency-sensitive LLM work for 50% cost reduction.

Anthropic's Message Batches API and OpenAI's Batch API allow up to 50%
discount on requests that don't need real-time responses (bulk document
analysis, nightly report generation, data enrichment).

This module provides a simple interface to queue batch jobs and poll for
results.  Jobs are stored in the database so they survive restarts.

Usage::

    from backend.src.modules.usage.batch_api import BatchClient

    client = BatchClient()

    # Queue work
    job_id = await client.submit_anthropic_batch([
        {"model": "claude-3-5-haiku-20241022", "max_tokens": 1024,
         "messages": [{"role": "user", "content": "Summarise this doc..."}]},
    ])

    # Check status later
    status = await client.check_status(job_id)
    if status["state"] == "completed":
        results = status["results"]
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

log = logging.getLogger(__name__)

# ── Batch job state (in-memory for now; can migrate to DB) ────────────────

_JOBS: dict[str, dict[str, Any]] = {}


class BatchClient:
    """Lightweight client for provider batch APIs.

    Supports:
    - Anthropic Message Batches (``/v1/messages/batches``)
    - OpenAI Batch API (``/v1/batches``)
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ) -> None:
        self._anthropic_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self._openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")

    # ── Anthropic batches ─────────────────────────────────────────────────

    async def submit_anthropic_batch(
        self,
        requests: list[dict[str, Any]],
        *,
        model: str = "claude-3-5-haiku-20241022",
    ) -> str:
        """Submit a batch of message requests to Anthropic.

        Parameters
        ----------
        requests:
            List of dicts, each containing ``messages``, and optionally
            ``system``, ``max_tokens``, ``temperature``.
        model:
            Default model for all requests in the batch.

        Returns
        -------
        str
            A local job ID for tracking.
        """
        job_id = str(uuid.uuid4())

        if not self._anthropic_key:
            log.warning("No Anthropic API key — batch job %s stored locally only", job_id)
            _JOBS[job_id] = {
                "provider": "anthropic",
                "state": "pending",
                "request_count": len(requests),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "remote_id": None,
                "results": None,
                "error": "No API key configured",
            }
            return job_id

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self._anthropic_key)

            # Build batch requests in Anthropic's format
            batch_requests = []
            for i, req in enumerate(requests):
                batch_requests.append({
                    "custom_id": f"req-{i}",
                    "params": {
                        "model": req.get("model", model),
                        "max_tokens": req.get("max_tokens", 1024),
                        "temperature": req.get("temperature", 0.2),
                        "messages": req["messages"],
                        **({"system": req["system"]} if "system" in req else {}),
                    },
                })

            batch = client.messages.batches.create(requests=batch_requests)
            remote_id = batch.id

            _JOBS[job_id] = {
                "provider": "anthropic",
                "state": "processing",
                "request_count": len(requests),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "remote_id": remote_id,
                "results": None,
                "error": None,
            }
            log.info(
                "Anthropic batch submitted: job=%s remote=%s requests=%d",
                job_id, remote_id, len(requests),
            )
            return job_id

        except Exception as exc:
            log.error("Failed to submit Anthropic batch: %s", exc)
            _JOBS[job_id] = {
                "provider": "anthropic",
                "state": "failed",
                "request_count": len(requests),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "remote_id": None,
                "results": None,
                "error": str(exc),
            }
            return job_id

    async def check_anthropic_status(self, job_id: str) -> dict[str, Any]:
        """Poll for the status of an Anthropic batch job."""
        job = _JOBS.get(job_id)
        if not job:
            return {"state": "not_found", "error": f"Job {job_id} not found"}

        if job["state"] in ("completed", "failed") or not job.get("remote_id"):
            return job

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self._anthropic_key)
            batch = client.messages.batches.retrieve(job["remote_id"])

            if batch.processing_status == "ended":
                # Collect results
                results = []
                for result in client.messages.batches.results(job["remote_id"]):
                    results.append({
                        "custom_id": result.custom_id,
                        "type": result.result.type,
                        "message": (
                            result.result.message.content[0].text
                            if hasattr(result.result, "message")
                            and result.result.message.content
                            else None
                        ),
                    })
                job["state"] = "completed"
                job["results"] = results
            else:
                job["state"] = "processing"

            return job

        except Exception as exc:
            log.error("Failed to check Anthropic batch status: %s", exc)
            return {**job, "error": str(exc)}

    # ── OpenAI batches ────────────────────────────────────────────────────

    async def submit_openai_batch(
        self,
        requests: list[dict[str, Any]],
        *,
        model: str = "gpt-4o-mini",
    ) -> str:
        """Submit a batch of chat completion requests to OpenAI.

        Returns a local job ID for tracking.
        """
        job_id = str(uuid.uuid4())

        if not self._openai_key:
            log.warning("No OpenAI API key — batch job %s stored locally only", job_id)
            _JOBS[job_id] = {
                "provider": "openai",
                "state": "pending",
                "request_count": len(requests),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "remote_id": None,
                "results": None,
                "error": "No API key configured",
            }
            return job_id

        try:
            import json
            import tempfile
            import openai

            client = openai.OpenAI(api_key=self._openai_key)

            # Write JSONL file for batch upload
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".jsonl", delete=False
            ) as f:
                for i, req in enumerate(requests):
                    line = {
                        "custom_id": f"req-{i}",
                        "method": "POST",
                        "url": "/v1/chat/completions",
                        "body": {
                            "model": req.get("model", model),
                            "max_tokens": req.get("max_tokens", 1024),
                            "temperature": req.get("temperature", 0.2),
                            "messages": req["messages"],
                        },
                    }
                    f.write(json.dumps(line) + "\n")
                jsonl_path = f.name

            # Upload file
            with open(jsonl_path, "rb") as f:
                batch_file = client.files.create(file=f, purpose="batch")

            # Create batch
            batch = client.batches.create(
                input_file_id=batch_file.id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
            )

            _JOBS[job_id] = {
                "provider": "openai",
                "state": "processing",
                "request_count": len(requests),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "remote_id": batch.id,
                "results": None,
                "error": None,
            }
            log.info(
                "OpenAI batch submitted: job=%s remote=%s requests=%d",
                job_id, batch.id, len(requests),
            )
            return job_id

        except Exception as exc:
            log.error("Failed to submit OpenAI batch: %s", exc)
            _JOBS[job_id] = {
                "provider": "openai",
                "state": "failed",
                "request_count": len(requests),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "remote_id": None,
                "results": None,
                "error": str(exc),
            }
            return job_id

    # ── Generic status check ──────────────────────────────────────────────

    async def check_status(self, job_id: str) -> dict[str, Any]:
        """Check the status of any batch job."""
        job = _JOBS.get(job_id)
        if not job:
            return {"state": "not_found"}

        if job["provider"] == "anthropic":
            return await self.check_anthropic_status(job_id)

        return job  # OpenAI status polling can be added similarly

    @staticmethod
    def list_jobs() -> list[dict[str, Any]]:
        """Return all tracked batch jobs."""
        return [
            {"job_id": k, **v}
            for k, v in sorted(
                _JOBS.items(),
                key=lambda x: x[1].get("created_at", ""),
                reverse=True,
            )
        ]
