#!/usr/bin/env python3
import argparse
import json
import os
from typing import Any

from agents_tooling import find_agent, prepare_adapters


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--env", default=os.getenv("AGENTS_ENV", "dev"))
    parser.add_argument("--pretty", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    agent_path, agent = find_agent(args.agent)
    adapters = prepare_adapters(agent, args.env)

    report: dict[str, Any] = {
        "agent": agent["name"],
        "role": agent.get("role"),
        "task": args.task,
        "env": args.env,
        "agent_path": str(agent_path),
        "tools": [],
    }

    for tool_id, config_ref, config_path, adapter in adapters:
        missing_env = adapter.verify_env()
        entry: dict[str, Any] = {
            "id": tool_id,
            "config_ref": config_ref,
            "config_path": str(config_path),
            "missing_env": missing_env,
        }
        if missing_env:
            entry["status"] = "blocked"
            entry["result"] = {
                "status": "skipped",
                "reason": f"missing env vars: {', '.join(missing_env)}",
            }
        else:
            result = adapter.run(args.task)
            entry["status"] = (
                result.get("status", "ok") if isinstance(result, dict) else "ok"
            )
            entry["result"] = result
        report["tools"].append(entry)

    encoded = json.dumps(report, indent=2)
    print(encoded)


if __name__ == "__main__":
    main()
