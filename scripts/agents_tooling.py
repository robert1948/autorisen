"""Lightweight adapters for agent tool execution."""
from __future__ import annotations

import json
import os
import pathlib
import time
import typing as t
import urllib.error
import urllib.request

import yaml

BASE_CONFIG_DIR = pathlib.Path("config")


class ToolAdapter:
    def __init__(self, tool_id: str, config: dict[str, t.Any]):
        self.tool_id = tool_id
        self.config = config

    def verify_env(self) -> list[str]:
        required = self.config.get("required_env", []) or []
        return [var for var in required if not os.getenv(var)]

    def run(self, task: str) -> dict[str, t.Any]:
        return {"status": "noop", "note": f"no runner for tool {self.tool_id}"}


class GitHubAdapter(ToolAdapter):
    def run(self, task: str) -> dict[str, t.Any]:
        missing = self.verify_env()
        payload: dict[str, t.Any] = {
            "status": "ready" if not missing else "blocked",
            "endpoint": self.config.get("endpoint"),
            "scopes": self.config.get("scopes", []),
        }
        if missing:
            payload["missing_env"] = missing
        else:
            payload["note"] = "Token present; API calls not executed in local runner."
        return payload


class HerokuAdapter(ToolAdapter):
    def run(self, task: str) -> dict[str, t.Any]:
        missing = self.verify_env()
        payload: dict[str, t.Any] = {
            "status": "ready" if not missing else "blocked",
            "endpoint": self.config.get("endpoint"),
            "registry": self.config.get("container_registry"),
        }
        if missing:
            payload["missing_env"] = missing
        else:
            payload["note"] = "Credentials present; deploy not triggered from runner."
        return payload


class HTTPAdapter(ToolAdapter):
    def run(self, task: str) -> dict[str, t.Any]:
        hosts: list[str] = self.config.get("allowed_hosts", []) or []
        timeouts = self.config.get("timeouts", {}) or {}
        connect_timeout = float(timeouts.get("connect", 5))
        read_timeout = float(timeouts.get("read", 10))
        results: list[dict[str, t.Any]] = []
        for host in hosts:
            if "*" in host:
                results.append({"host": host, "status": "skipped", "reason": "wildcard host not probed"})
                continue
            url = host.rstrip("/") + "/api/health"
            start = time.perf_counter()
            try:
                with urllib.request.urlopen(url, timeout=max(connect_timeout, read_timeout)) as response:
                    body = response.read()
                    latency_ms = (time.perf_counter() - start) * 1000
                    data: t.Any
                    try:
                        data = json.loads(body.decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        data = body.decode("utf-8", errors="replace")
                    results.append(
                        {
                            "host": host,
                            "status": "ok" if response.status == 200 else "warn",
                            "code": response.status,
                            "latency_ms": round(latency_ms, 2),
                            "body": data,
                        }
                    )
            except urllib.error.URLError as exc:  # pragma: no cover - network errors expected
                results.append({"host": host, "status": "error", "reason": str(exc)})
        return {"status": "checked", "probes": results}


def load_yaml(path: pathlib.Path) -> dict[str, t.Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_agent(agent_path: pathlib.Path) -> dict[str, t.Any]:
    return load_yaml(agent_path)


def find_agent(agent_name: str) -> tuple[pathlib.Path, dict[str, t.Any]]:
    for path in pathlib.Path("agents").rglob("agent.yaml"):
        data = load_agent(path)
        if data.get("name") == agent_name:
            return path, data
    raise SystemExit(f"agent {agent_name} not found")


def resolve_tool_config(config_ref: str, env: str) -> pathlib.Path:
    path = BASE_CONFIG_DIR / env / "tools" / f"{config_ref}.yaml"
    if not path.exists():
        raise SystemExit(f"config {path} not found")
    return path


def build_adapter(tool_id: str, config_data: dict[str, t.Any]) -> ToolAdapter:
    if tool_id == "github":
        return GitHubAdapter(tool_id, config_data)
    if tool_id == "heroku":
        return HerokuAdapter(tool_id, config_data)
    if tool_id == "http":
        return HTTPAdapter(tool_id, config_data)
    return ToolAdapter(tool_id, config_data)


def prepare_adapters(agent: dict[str, t.Any], env: str) -> list[tuple[str, str, pathlib.Path, ToolAdapter]]:
    adapters: list[tuple[str, str, pathlib.Path, ToolAdapter]] = []
    for tool in agent.get("tools", []) or []:
        tool_id = tool.get("id")
        config_ref = tool.get("config_ref")
        if not tool_id or not config_ref:
            raise SystemExit("tool entries must include id and config_ref")
        config_path = resolve_tool_config(config_ref, env)
        config_data = load_yaml(config_path)
        adapters.append((tool_id, config_ref, config_path, build_adapter(tool_id, config_data)))
    return adapters


__all__ = [
    "prepare_adapters",
    "find_agent",
]
