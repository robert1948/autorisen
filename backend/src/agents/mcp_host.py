# backend/src/agents/mcp_host.py
from __future__ import annotations

import importlib
import inspect
import logging
import os
import pathlib
from typing import Any, Dict, Optional, TYPE_CHECKING, cast

log = logging.getLogger("mcp-host")


class MCPConfigError(RuntimeError): ...


# ---- Type-checker friendliness (no hard dependency at import time) ----
if TYPE_CHECKING:  # pragma: no cover

    class _AgentStub:
        def respond(self, prompt: str): ...

    AgentT = _AgentStub
else:
    AgentT = Any


def _repo_root() -> pathlib.Path:
    # File: backend/src/agents/mcp_host.py -> repo root is parents[3]
    return pathlib.Path(__file__).resolve().parents[3]


def _load_registry() -> Dict[str, Any]:
    env = os.getenv("ENV", "dev").lower()
    cfg = _repo_root() / "config" / "mcp" / f"servers.{env}.yaml"
    if not cfg.exists():
        raise MCPConfigError(f"MCP registry not found: {cfg}")
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise MCPConfigError(
            "PyYAML is required to load MCP registry. pip install pyyaml"
        ) from exc
    return cast(Dict[str, Any], yaml.safe_load(cfg.read_text()))


def _import_openai_agents() -> tuple[Any, Any, Any]:
    """
    Import OpenAI + Agents at runtime so this module can be imported
    even if the optional dependency isn't installed.

    Returns: (OpenAI, Agent_or_factory, agents_module)
    """
    try:
        openai_mod = importlib.import_module("openai")
    except ModuleNotFoundError as exc:
        raise MCPConfigError(
            "OpenAI SDK not available. Install it first:\n" "  pip install openai"
        ) from exc

    agents_mod = None
    last_exc: Optional[Exception] = None
    for module_name in ("openai.agents", "agents"):
        try:
            agents_mod = importlib.import_module(module_name)
            break
        except ModuleNotFoundError as exc:
            last_exc = exc
            continue

    if agents_mod is None:
        raise MCPConfigError(
            "OpenAI Agents SDK not available. Install it first:\n"
            "  pip install openai-agents\n"
            "or upgrade 'openai' to a version that exposes 'openai.agents'."
        ) from last_exc

    OpenAI = getattr(openai_mod, "OpenAI", None)
    Agent_or_factory = getattr(agents_mod, "Agent", None) or getattr(
        agents_mod, "create_agent", None
    )

    if OpenAI is None or Agent_or_factory is None:
        raise MCPConfigError(
            "Your OpenAI package does not expose the expected Agents API. "
            "Upgrade to a build that includes 'openai.agents'."
        )

    return OpenAI, Agent_or_factory, agents_mod


def _build_mcp_servers(registry: Dict[str, Any], agents_mod: Any) -> list[Any]:
    servers: list[Any] = []
    mcp_server_attr = getattr(agents_mod, "MCPServer", None)
    transport_factory = (
        getattr(mcp_server_attr, "transport", None) if mcp_server_attr else None
    )
    mcp_module = None

    # Newer "agents" packages expose transports via agents.mcp.MCPServer* classes.
    if transport_factory is None:
        for mod_name in (
            getattr(getattr(agents_mod, "mcp", None), "__name__", None),
            f"{getattr(agents_mod, '__name__', 'agents')}.mcp",
            "agents.mcp",
            "openai.agents.mcp",
        ):
            if not mod_name:
                continue
            try:
                mcp_module = importlib.import_module(mod_name)
                break
            except ModuleNotFoundError:
                continue

    for sid, s in (registry.get("servers") or {}).items():
        t = s.get("transport")
        if transport_factory:
            server_obj: Any | None = None
            if t == "stdio":
                server_obj = transport_factory(
                    "stdio",
                    command=s["command"],
                    args=s.get("args", []),
                    id=sid,
                    env=s.get("env", {}),
                )
            elif t == "http":
                server_obj = transport_factory(
                    "http",
                    url=s["url"],
                    id=sid,
                    headers=s.get("headers", {}),
                )
            else:
                log.warning("Unknown MCP transport for %s: %r", sid, t)

            if server_obj is not None and getattr(server_obj, "id", None) is None:
                try:
                    setattr(server_obj, "id", sid)
                except Exception:
                    pass
            if server_obj is not None:
                servers.append(server_obj)
            continue

        if not mcp_module:
            raise MCPConfigError(
                "Installed Agents package does not expose MCP transports. "
                "Upgrade to a newer build with 'agents.mcp'."
            )

        if t == "stdio":
            stdio_cls = getattr(mcp_module, "MCPServerStdio", None)
            if not stdio_cls:
                raise MCPConfigError("Agents SDK missing MCPServerStdio transport")
            params = {"command": s["command"]}
            if "args" in s:
                params["args"] = s["args"]
            if "env" in s:
                params["env"] = s["env"]
            if "cwd" in s:
                params["cwd"] = s["cwd"]
            if "encoding" in s:
                params["encoding"] = s["encoding"]
            if "encoding_error_handler" in s:
                params["encoding_error_handler"] = s["encoding_error_handler"]
            server_obj = stdio_cls(params=params, name=sid)
            if getattr(server_obj, "id", None) is None:
                setattr(server_obj, "id", sid)
            servers.append(server_obj)
        elif t == "http":
            sse_cls = getattr(mcp_module, "MCPServerSse", None)
            if not sse_cls:
                raise MCPConfigError("Agents SDK missing MCPServerSse transport")
            params = {"url": s["url"]}
            if "headers" in s:
                params["headers"] = s["headers"]
            if "timeout" in s:
                params["timeout"] = s["timeout"]
            if "sse_read_timeout" in s:
                params["sse_read_timeout"] = s["sse_read_timeout"]
            server_obj = sse_cls(params=params, name=sid)
            if getattr(server_obj, "id", None) is None:
                setattr(server_obj, "id", sid)
            servers.append(server_obj)
        elif t == "streamable_http":
            stream_cls = getattr(mcp_module, "MCPServerStreamableHttp", None)
            if not stream_cls:
                raise MCPConfigError(
                    "Agents SDK missing MCPServerStreamableHttp transport"
                )
            params = {"url": s["url"]}
            if "headers" in s:
                params["headers"] = s["headers"]
            if "timeout" in s:
                params["timeout"] = s["timeout"]
            if "sse_read_timeout" in s:
                params["sse_read_timeout"] = s["sse_read_timeout"]
            if "terminate_on_close" in s:
                params["terminate_on_close"] = s["terminate_on_close"]
            server_obj = stream_cls(params=params, name=sid)
            if getattr(server_obj, "id", None) is None:
                setattr(server_obj, "id", sid)
            servers.append(server_obj)
        else:
            log.warning("Unknown MCP transport for %s: %r", sid, t)
    return servers


def _init_openai_agents(registry: Dict[str, Any]) -> tuple[Any, AgentT, Any]:
    """
    Returns (OpenAI client, Agent) configured with multiple MCP servers.
    Handles both API shapes:
      - class Agent(...), and
      - factory create_agent(...).
    """
    OpenAI, Agent_or_factory, agents_mod = _import_openai_agents()
    servers = _build_mcp_servers(registry, agents_mod)

    # Prepare kwargs used by both shapes
    common_kwargs = dict(
        name="capecontrol-agent",
        mcp_servers=servers,
        instructions=(
            "You are CapeControl’s internal ops agent. "
            "Prefer fs-ro for read-only repo queries; use heroku-stg only for "
            "staging releases/logs. Never touch production."
        ),
    )

    # If it's callable, we can just call it. Works for both class and factory.
    try:
        agent_obj = Agent_or_factory(**common_kwargs)  # type: ignore[call-arg]
    except TypeError:
        # Some older shapes use different argument names. Try a fallback.
        alt_kwargs = dict(
            title=common_kwargs["name"],
            servers=common_kwargs["mcp_servers"],
            system_prompt=common_kwargs["instructions"],
        )
        agent_obj = Agent_or_factory(**alt_kwargs)  # type: ignore[call-arg]

    client = OpenAI()  # reads OPENAI_API_KEY
    return client, cast(AgentT, agent_obj), agents_mod


def _extract_text(resp: Any) -> str:
    """Normalize text output across preview shapes."""
    if isinstance(resp, str):
        return resp
    for attr in ("output_text", "text", "content", "message"):
        if hasattr(resp, attr):
            try:
                val = getattr(resp, attr)
                return val if isinstance(val, str) else str(val)
            except Exception:
                continue
    return str(resp)


async def _ensure_mcp_servers_connected(agent: AgentT) -> None:
    """Connect MCP servers once prior to agent usage."""
    servers = getattr(agent, "mcp_servers", [])
    disabled: dict[str, str] = {}
    active_servers: list[Any] = []
    for server in servers:
        server_id = getattr(server, "id", getattr(server, "name", repr(server)))
        if getattr(server, "_autolocal_connected", False):
            active_servers.append(server)
            continue
        connect_fn = getattr(server, "connect", None)
        if not callable(connect_fn):
            setattr(server, "_autolocal_connected", True)
            active_servers.append(server)
            continue
        try:
            res = connect_fn()
            if inspect.isawaitable(res):
                await res
            setattr(server, "_autolocal_connected", True)
            active_servers.append(server)
        except Exception as exc:
            if isinstance(exc, FileNotFoundError) or getattr(exc, "errno", None) == 2:
                reason = f"Executable not found: {exc}"
            else:
                reason = f"Connection failed: {type(exc).__name__}: {exc}"
            log.warning("Skipping MCP server %s: %s", server_id, reason)
            disabled[str(server_id)] = reason
            continue

    if disabled:
        setattr(agent, "_autolocal_disabled_mcp", disabled)
    if len(active_servers) != len(servers):
        setattr(agent, "mcp_servers", active_servers)


async def _invoke_agent(
    agent: AgentT, prompt: str, agents_mod: Any | None = None
) -> str:
    """
    Try several common method names exposed by different agent builds.
    Supports both legacy synchronous APIs and newer coroutine-based runners.
    """
    await _ensure_mcp_servers_connected(agent)
    for meth in ("respond", "ask", "run", "invoke"):
        fn = getattr(agent, meth, None)
        if callable(fn):
            try:
                result = fn(prompt)
            except TypeError:
                # Signature mismatch; try next option.
                continue
            if inspect.isawaitable(result):
                result = await result
            return _extract_text(result)

    # Newer SDKs expose Runner/AgentRunner helpers instead of direct methods.
    if agents_mod is not None:
        runner_cls = getattr(agents_mod, "Runner", None)
        if runner_cls is not None and hasattr(runner_cls, "run"):
            run_result = runner_cls.run(agent, prompt)
            if inspect.isawaitable(run_result):
                run_result = await run_result
            final_output = getattr(run_result, "final_output", None)
            if final_output is not None:
                return _extract_text(final_output)
            return _extract_text(run_result)

        agent_runner_cls = getattr(agents_mod, "AgentRunner", None)
        if agent_runner_cls is not None:
            try:
                runner = agent_runner_cls()
            except Exception:
                runner = None
            if runner is not None and hasattr(runner, "run"):
                run_result = runner.run(agent, prompt)
                if inspect.isawaitable(run_result):
                    run_result = await run_result
                final_output = getattr(run_result, "final_output", None)
                if final_output is not None:
                    return _extract_text(final_output)
                return _extract_text(run_result)

    # Some modules expose a module-level factory for responses
    # e.g., agents_mod.respond(agent, prompt) — not typical, but guard anyway.
    return _extract_text(agent)  # last resort


class MCPHost:
    def __init__(self) -> None:
        self.enabled = os.getenv("ENABLE_MCP_HOST", "0") == "1"
        self.client: Optional[Any] = None
        self.agent: Optional[AgentT] = None
        self.agents_module: Optional[Any] = None
        self.ready: bool = False
        self.last_error: Optional[str] = None

    def start(self) -> None:
        self.ready = False
        self.last_error = None
        if not self.enabled:
            log.info("MCP host disabled (ENABLE_MCP_HOST!=1)")
            self.last_error = "ENABLE_MCP_HOST flag is not set"
            self.client = None
            self.agent = None
            self.agents_module = None
            return
        try:
            registry = _load_registry()
            self.client, self.agent, self.agents_module = _init_openai_agents(registry)
            try:
                count = len(getattr(self.agent, "mcp_servers", []))  # type: ignore[arg-type]
            except Exception:
                count = 0
            log.info("MCP host started with %d servers", count)
            self.ready = True
        except MCPConfigError as exc:
            self.client = None
            self.agent = None
            self.agents_module = None
            self.last_error = str(exc)
            self.ready = False
            raise
        except Exception as exc:  # pragma: no cover
            self.client = None
            self.agent = None
            self.agents_module = None
            self.last_error = str(exc)
            self.ready = False
            raise

    async def ask(self, prompt: str) -> str:
        if not self.enabled or not self.ready or not self.agent:
            raise RuntimeError("MCP host not enabled/initialized")
        return await _invoke_agent(self.agent, prompt, self.agents_module)


mcp_host = MCPHost()
