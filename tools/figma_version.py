#!/usr/bin/env python3
"""
Maintains docs/figma/version.json and validates version during CI.

Usage:
  figma_version.py set   --version v0.2 --file docs/figma/version.json
  figma_version.py check --expect v0.2  --file docs/figma/version.json
"""
import argparse, json, os, sys


def cmd_set(path, version):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"design_version": version}, f, indent=2)
    print(version)


def cmd_check(path, expect):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        actual = data.get("design_version")
    except Exception:
        print(f"ERR: missing or invalid {path}", file=sys.stderr)
        sys.exit(2)
    if not expect:
        print("WARN: CI_EXPECT_FIGMA_VERSION not set; skipping strict check")
        return
    if actual != expect:
        print(
            f"ERR: design version mismatch (actual {actual} != expected {expect})",
            file=sys.stderr,
        )
        sys.exit(3)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("set")
    s.add_argument("--version", required=True)
    s.add_argument("--file", required=True)

    c = sub.add_parser("check")
    c.add_argument("--expect", default="")
    c.add_argument("--file", required=True)

    a = ap.parse_args()
    if a.cmd == "set":
        cmd_set(a.file, a.version)
    else:
        cmd_check(a.file, a.expect)


if __name__ == "__main__":
    main()
