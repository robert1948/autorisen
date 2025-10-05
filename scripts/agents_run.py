#!/usr/bin/env python3
import argparse
import glob
import json
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("--agent", required=True)
parser.add_argument("--task", required=True)
args = parser.parse_args()

paths = glob.glob("agents/**/agent.yaml", recursive=True)
selected = None
for path in paths:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data.get("name") == args.agent:
        selected = data
        break

if not selected:
    raise SystemExit(f"agent {args.agent} not found")

print(
    json.dumps(
        {
            "agent": selected["name"],
            "role": selected["role"],
            "task": args.task,
            "tools": selected.get("policies", {}).get("allow_tools", []),
        },
        indent=2,
    )
)
