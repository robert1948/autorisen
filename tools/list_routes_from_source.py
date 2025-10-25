#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List likely routes by scanning client/src for React Router and anchor usage.
Stdlib only; no dependencies.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # repo root
SRC = ROOT / "client" / "src"

# Regexes to catch common patterns
ROUTE_PATH = re.compile(r'path\s*[:=]\s*["\'](/[^"\']*)["\']')
LINK_TO = re.compile(r'<Link\s+[^>]*to\s*=\s*["\'](/[^"\']*)["\']')
HREF = re.compile(r'href\s*=\s*["\'](/[^"\']*)["\']')


def scan():
    routes = set()
    for p in SRC.rglob("*"):
        if p.suffix.lower() not in {".tsx", ".jsx", ".ts", ".js"}:
            continue
        try:
            text = p.read_text("utf-8", errors="ignore")
        except Exception:
            continue
        for rx in (ROUTE_PATH, LINK_TO, HREF):
            routes.update(rx.findall(text))
    # Normalize: drop trailing slash (except root), sort
    norm = set()
    for r in routes:
        if r != "/" and r.endswith("/"):
            r = r[:-1]
        norm.add(r)
    print("Discovered (from source):")
    for r in sorted(norm):
        print(" -", r)


if __name__ == "__main__":
    if not SRC.exists():
        print(f"client/src not found at: {SRC}", file=sys.stderr)
        sys.exit(2)
    scan()
