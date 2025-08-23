#!/usr/bin/env python3
"""
Simple OpenAPI diff script.
Exits with non-zero if any path present in baseline is missing from current (conservative breaking-change check).

Usage:
  python scripts/openapi_diff.py --baseline docs/openapi_baseline.json --current openapi_current.json

If baseline file is missing, the script exits successfully (no baseline to compare).
"""
import argparse
import json
import sys
from pathlib import Path


def load_json(path: Path):
    if not path.exists():
        return None
    with path.open('r') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--current', required=True)
    args = parser.parse_args()

    baseline_path = Path(args.baseline)
    current_path = Path(args.current)

    baseline = load_json(baseline_path)
    if baseline is None:
        print(f"No baseline found at {baseline_path}; skipping OpenAPI diff.")
        return 0

    current = load_json(current_path)
    if current is None:
        print(f"Current OpenAPI file not found at {current_path}")
        return 2

    base_paths = set(baseline.get('paths', {}).keys())
    cur_paths = set(current.get('paths', {}).keys())

    removed = base_paths - cur_paths
    added = cur_paths - base_paths

    if not removed:
        print("No removed paths detected in OpenAPI comparison.")
    else:
        print("Detected removed paths (breaking):")
        for p in sorted(removed):
            print("  -", p)

    print(f"Paths added: {len(added)}; paths removed: {len(removed)}")

    if removed:
        print("Failing: breaking OpenAPI changes detected.")
        return 3

    print("OpenAPI diff OK.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
