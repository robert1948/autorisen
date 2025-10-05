#!/usr/bin/env python3
import sys
import yaml
import pathlib

SCHEMA_KEYS = {"name", "role", "model", "policies", "context"}


def load_yaml(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main(registry_path: str) -> None:
    reg_path = pathlib.Path(registry_path)
    registry = load_yaml(reg_path)
    ok = True
    for item in registry.get("agents", []):
        agent_path = pathlib.Path(item["path"])
        if not agent_path.exists():
            print(f"❌ Missing: {agent_path}")
            ok = False
            continue
        agent = load_yaml(agent_path)
        missing = SCHEMA_KEYS - set(agent.keys())
        if missing:
            print(f"❌ {agent_path}: missing keys {sorted(missing)}")
            ok = False
        else:
            print(f"✅ {agent_path}: schema ok")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(sys.argv[1])
