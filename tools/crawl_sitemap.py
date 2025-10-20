#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight same-origin crawler for auditing navigation paths (SPA-friendly, stdlib only).

Usage:
  python3 tools/crawl_sitemap.py http://localhost:3000
  python3 tools/crawl_sitemap.py https://dev.cape-control.com
  python3 tools/crawl_sitemap.py https://cape-control.com
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict, deque
from html.parser import HTMLParser
from typing import Dict, Iterable, List, Optional, Set, Tuple
from urllib import error, parse, request

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) autorisen-stdlib-crawler/1.3"
DEFAULT_TIMEOUT = 8.0

# Candidate routes to probe if bundle mining yields nothing (safe, tweak as needed)
FALLBACK_CANDIDATES: Set[str] = {
    "/", "/about", "/login", "/register", "/subscribe",
    "/register?role=user", "/register?role=developer",
}

# Strings in JS bundles that *look* like app routes: "/about", "/login", etc.
ROUTE_PATTERN = re.compile(r'"(/[^"?#]+)"')

# Some CDNs require Accept; avoid "br" to skip brotli since stdlib can't decode it.
COMMON_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
}


class PageExtractor(HTMLParser):
    """Extract anchor targets and script sources from HTML documents."""
    def __init__(self) -> None:
        super().__init__()
        self.links: List[str] = []
        self.scripts: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        t = tag.lower()
        if t == "a":
            for k, v in attrs:
                if k.lower() == "href" and v:
                    self.links.append(v)
        elif t == "script":
            for k, v in attrs:
                if k.lower() == "src" and v:
                    self.scripts.append(v)


def fetch(url: str, timeout: float = DEFAULT_TIMEOUT) -> Optional[str]:
    """Return the HTML/text body at `url` or `None` on failure."""
    req = request.Request(url, headers=COMMON_HEADERS)
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            ctype = resp.headers.get("Content-Type", "")
            if "text/html" not in ctype and "text/plain" not in ctype and "javascript" not in ctype:
                return None
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except (error.HTTPError, error.URLError, TimeoutError):
        return None


def head_or_get(url: str, timeout: float = DEFAULT_TIMEOUT) -> int:
    """Return HTTP status code; try HEAD first, then GET on 405 or error."""
    # Try HEAD
    try:
        req = request.Request(url, method="HEAD", headers=COMMON_HEADERS)
        with request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode()
    except error.HTTPError as e:
        if e.code != 405:
            return e.code
        # fall through to GET on 405
    except Exception:
        # fall through to GET on any non-HTTPError issue with HEAD
        pass

    # Try GET
    try:
        req = request.Request(url, method="GET", headers=COMMON_HEADERS)
        with request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode()
    except error.HTTPError as e:
        return e.code
    except Exception:
        return 0  # network/other error


def normalize(base_url: str, href: str, domain: str) -> Optional[str]:
    """Normalize a link into a same-domain path we can crawl."""
    if not href:
        return None
    resolved = parse.urljoin(base_url, href)
    p = parse.urlparse(resolved)

    # same-origin only
    if p.netloc != domain:
        return None

    # ignore non-http schemes
    if p.scheme not in ("http", "https", ""):
        return None

    path = p.path or "/"

    # trim trailing slash (except root)
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]

    # Preserve role query on /register
    if path == "/register" and p.query:
        q = parse.parse_qs(p.query, keep_blank_values=True)
        if "role" in q and q["role"]:
            return f"{path}?role={q['role'][0]}"

    return path


def crawl(base_url: str, timeout: float = DEFAULT_TIMEOUT) -> Tuple[Dict[str, List[str]], Set[str]]:
    """Breadth-first crawl returning navigation graph and bundle-derived (reachable) routes."""
    origin = base_url.rstrip("/")
    domain = parse.urlparse(origin).netloc

    seen: Set[str] = set()
    graph: Dict[str, List[str]] = defaultdict(list)
    q: deque[str] = deque(["/"])
    bundle_sources: Set[str] = set()

    while q:
        cur = q.popleft()
        if cur in seen:
            continue
        seen.add(cur)

        html = fetch(parse.urljoin(origin, cur), timeout=timeout)
        if html is None:
            graph.setdefault(cur, [])
            continue

        parser = PageExtractor()
        parser.feed(html)
        graph.setdefault(cur, [])

        for src in set(parser.scripts):
            bundle_sources.add(parse.urljoin(origin, src))

        for raw in parser.links:
            n = normalize(origin, raw, domain)
            if not n:
                continue
            if n not in graph[cur]:
                graph[cur].append(n)
            if n not in seen:
                q.append(n)

    # Try to mine routes from JS bundles; if none, fall back to probing known candidates
    bundle_routes = discover_bundle_routes(origin, bundle_sources, timeout)
    if not bundle_routes:
        bundle_routes = probe_candidates(origin, FALLBACK_CANDIDATES, timeout)

    return dict(graph), bundle_routes


def discover_bundle_routes(base_url: str, script_urls: Set[str], timeout: float) -> Set[str]:
    """Fetch static bundles and mine them for likely SPA routes, then keep only reachable ones."""
    candidates: Set[str] = set()

    for src in script_urls:
        # Focus on app bundles; skip obvious non-code assets
        if not (src.endswith(".js") or "/assets/" in src or "/static/" in src):
            continue
        text = fetch(src, timeout=timeout)
        if not text:
            continue
        for m in ROUTE_PATTERN.findall(text):
            leaf = m.split("/")[-1]
            if "." in leaf:  # e.g., "/logo.svg"
                continue
            if m.startswith(("/assets", "/static", "/img", "/images", "/fonts")):
                continue
            candidates.add(m)

    # Add role-split variants if /register exists
    if "/register" in candidates:
        candidates.update({"/register?role=user", "/register?role=developer"})

    return probe_candidates(base_url, candidates, timeout)


def probe_candidates(base_url: str, candidates: Set[str], timeout: float) -> Set[str]:
    """Return the subset of candidates that respond with 2xx/3xx."""
    reachable: Set[str] = set()
    for p in sorted(candidates):
        url = parse.urljoin(base_url + "/", p.lstrip("/"))
        code = head_or_get(url, timeout=timeout)
        if code and 200 <= code < 400:
            reachable.add(p)
    return reachable


def iter_routes(graph: Dict[str, List[str]]) -> Iterable[str]:
    """Yield the set of unique routes discovered in the anchor graph."""
    routes: Set[str] = set(graph.keys())
    for children in graph.values():
        routes.update(children)
    return sorted(routes)


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("Usage: python3 tools/crawl_sitemap.py <base_url>")
        return 2

    base_url = argv[1].strip()
    graph, bundle_routes = crawl(base_url)

    print("Discovered routes (anchors):")
    discovered = set(iter_routes(graph))
    for route in sorted(discovered):
        print(f" - {route}")

    remaining = sorted(bundle_routes - discovered)
    if remaining:
        print("\nReachable routes (bundle/fallback probe):")
        for route in remaining:
            print(f" - {route}")

    print("\nNavigation edges (anchor graph):")
    for src in sorted(graph.keys()):
        targets = ", ".join(graph[src]) if graph[src] else "(none)"
        print(f" {src} -> {targets}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
