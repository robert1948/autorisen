#!/usr/bin/env python3
"""
Lightweight sitemap crawler for local/dev/prod.

Features
- Finds sitemaps via robots.txt and common fallbacks
- Handles sitemap indexes + urlsets (namespace-agnostic)
- Retries with backoff, timeouts, polite pacing
- Optional SEO lint (title + meta description) if beautifulsoup4 is installed
- Outputs: docs/crawl/<timestamp>-<label>-<host>.md and .csv
- Optional CI gates: --fail-on-error, --require-title, --require-description
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter

try:
    # urllib3 Retry location differs by version
    from urllib3.util.retry import Retry  # type: ignore
except Exception:  # pragma: no cover
    Retry = None  # fallback: no retries

try:
    from bs4 import BeautifulSoup  # SEO lint optional
except Exception:
    BeautifulSoup = None


# ----------------------- HTTP utils ----------------------- #
import inspect  # add near the top with other imports


def _build_retry(total_retries: int):
    """
    Build a urllib3 Retry that works across versions without angering type checkers.
    We inspect the constructor signature and only pass supported parameters.
    """
    if not Retry or total_retries <= 0:
        return None

    status = frozenset({429, 500, 502, 503, 504})
    methods = frozenset({"GET", "HEAD"})

    base = {
        "total": total_retries,
        "connect": total_retries,
        "read": total_retries,
        "backoff_factor": 0.5,
    }

    # Introspect which kwargs this Retry variant accepts
    try:
        sig = inspect.signature(Retry)  # type: ignore[arg-type]
        accepts = {p.name for p in sig.parameters.values()}
    except Exception:
        accepts = set()

    kwargs = dict(base)
    if "status_forcelist" in accepts:
        kwargs["status_forcelist"] = status

    # Prefer new API if available
    if "allowed_methods" in accepts:
        kwargs["allowed_methods"] = methods
        if "raise_on_status" in accepts:
            kwargs["raise_on_status"] = False
        return Retry(**kwargs)  # type: ignore[call-arg]

    # Fall back to old API
    if "method_whitelist" in accepts:
        kwargs["method_whitelist"] = methods  # type: ignore[dict-item]
        return Retry(**kwargs)  # type: ignore[call-arg]

    # Very old versions: no method controls, maybe no forcelist
    kwargs.pop("status_forcelist", None)
    return Retry(**kwargs)  # type: ignore[call-arg]


def make_session(user_agent: str, total_retries: int = 3) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": user_agent})
    r = _build_retry(total_retries)
    if r:
        adapter = HTTPAdapter(max_retries=r, pool_connections=50, pool_maxsize=50)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
    return s


def _get(session: requests.Session, url: str, timeout: int) -> requests.Response:
    r = session.get(url, timeout=timeout)
    r.raise_for_status()
    return r


def _is_html(content_type: str | None) -> bool:
    if not content_type:
        return False
    ct = content_type.lower()
    return ("text/html" in ct) or ("application/xhtml+xml" in ct)


# ----------------------- Sitemap discovery ----------------------- #
_ROBOTS_RE = re.compile(r"(?i)^\s*sitemap:\s*(?P<url>\S+)\s*$")


def discover_sitemaps(
    base_url: str, session: requests.Session, timeout: int
) -> List[str]:
    base = base_url.rstrip("/") + "/"
    robots_url = urljoin(base, "robots.txt")
    sitemaps: List[str] = []
    try:
        r = _get(session, robots_url, timeout)
        for line in r.text.splitlines():
            m = _ROBOTS_RE.match(line.strip())
            if m:
                sitemaps.append(m.group("url").strip())
    except Exception:
        pass
    # common fallbacks
    for suffix in ("sitemap.xml", "sitemap_index.xml", "sitemap.txt"):
        sitemaps.append(urljoin(base, suffix))
    # de-dupe preserving order
    seen, out = set(), []
    for s in sitemaps:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def parse_sitemap_urls(
    map_url: str, session: requests.Session, timeout: int, limit: int | None = None
) -> List[str]:
    """
    Parse a sitemap or sitemap index. Returns list of URLs.
    Supports: xml urlset, xml sitemapindex, and plain text (newline URLs).
    """
    urls: List[str] = []
    try:
        r = _get(session, map_url, timeout)
        content_type = (r.headers.get("content-type", "") or "").lower()
        data = r.content

        # If text/plain → treat as newline-separated URLs
        if "text/plain" in content_type or map_url.endswith(".txt"):
            for line in r.text.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
            return urls[:limit] if limit else urls

        # Try XML parse
        import xml.etree.ElementTree as ET  # local import to avoid global cost

        root = ET.fromstring(data)

        def tagname(t: str) -> str:
            # namespace-agnostic
            return t.split("}")[-1].lower()

        if tagname(root.tag) == "sitemapindex":
            for child in root:
                if tagname(child.tag) == "sitemap":
                    loc = None
                    for elem in child:
                        if tagname(elem.tag) == "loc":
                            loc = (elem.text or "").strip()
                            break
                    if loc:
                        urls.extend(parse_sitemap_urls(loc, session, timeout, limit))
            return urls[:limit] if limit else urls

        if tagname(root.tag) == "urlset":
            for child in root:
                if tagname(child.tag) == "url":
                    loc = None
                    for elem in child:
                        if tagname(elem.tag) == "loc":
                            loc = (elem.text or "").strip()
                            break
                    if loc:
                        urls.append(loc)
            return urls[:limit] if limit else urls

        # Fallback: not recognized XML → single target
        return [map_url]
    except Exception:
        # Non-XML or failure: treat as single target to avoid silent miss
        return [map_url]


# ----------------------- Crawl / Lint ----------------------- #
def seo_lint(html: str) -> Tuple[str, str]:
    """Return (title, meta_description) safely across bs4 versions."""
    if not BeautifulSoup:
        return ("", "")

    soup = BeautifulSoup(html, "html.parser")

    # --- title ---
    title = ""
    if soup.title:
        t = soup.title.string or soup.title.get_text()
        if t:
            title = str(t).strip()

    # --- description ---
    import re as _re

    md = soup.find("meta", attrs={"name": _re.compile(r"^description$", _re.I)})
    if not md:
        md = soup.find(
            "meta", attrs={"property": _re.compile(r"^og:description$", _re.I)}
        )

    def _textify(v) -> str:
        """Handle AttributeValueList, list, tuple, NavigableString, etc."""
        if v is None:
            return ""
        if isinstance(v, (list, tuple)):
            return " ".join(str(x) for x in v if x).strip()
        return str(v).strip()

    desc = _textify(md.get("content") if md else "")

    return (title, desc)


def fetch_url(
    session: requests.Session, url: str, do_seo: bool, timeout: int
) -> Tuple[str, int, str, str, str, bool]:
    """
    Returns tuple:
      (url, status_code, error, title, description, is_html)
    """
    try:
        r = _get(session, url, timeout)
        ct = r.headers.get("content-type", "")
        is_html = _is_html(ct)
        title, desc = ("", "")
        if do_seo and is_html:
            title, desc = seo_lint(r.text)
        return (url, r.status_code, "", title, desc, is_html)
    except requests.HTTPError as e:
        code = e.response.status_code if e.response else 0
        return (url, code, f"HTTPError: {code}", "", "", False)
    except Exception as e:
        return (url, 0, f"{e.__class__.__name__}: {e}", "", "", False)


# ----------------------- Main ----------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--base-url", required=True, help="Base site, e.g. http://localhost:3000"
    )
    ap.add_argument(
        "--outdir", default="docs/crawl", help="Output directory for reports"
    )
    ap.add_argument("--label", default="local", help="Label for report filenames")
    ap.add_argument("--max", type=int, default=2000, help="Max pages to fetch")
    ap.add_argument("--concurrency", type=int, default=10, help="Concurrent workers")
    ap.add_argument(
        "--no-seo", action="store_true", help="Disable SEO lint (title/description)"
    )
    ap.add_argument("--retries", type=int, default=3, help="Total HTTP retries")
    ap.add_argument("--timeout", type=int, default=20, help="HTTP timeout (seconds)")
    ap.add_argument(
        "--sleep", type=float, default=0.0, help="Per-request delay (seconds)"
    )
    # CI gates (optional)
    ap.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit non-zero if any non-2xx/3xx response",
    )
    ap.add_argument(
        "--require-title",
        action="store_true",
        help="Exit non-zero if any HTML page lacks <title>",
    )
    ap.add_argument(
        "--require-description",
        action="store_true",
        help="Exit non-zero if any HTML page lacks meta description",
    )
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    host = urlparse(args.base_url).netloc or "localhost"
    base = args.base_url.rstrip("/") + "/"

    md_path = os.path.join(args.outdir, f"{ts}-{args.label}-{host}.md")
    csv_path = os.path.join(args.outdir, f"{ts}-{args.label}-{host}.csv")

    ua = f"autolocal-crawler/1.2 (+{host}; label={args.label})"
    session = make_session(ua, total_retries=args.retries)

    # 1) discover sitemaps
    sitemaps = discover_sitemaps(base, session, timeout=args.timeout)

    # 2) gather URLs
    urls: List[str] = []
    for sm in sitemaps:
        urls.extend(
            parse_sitemap_urls(sm, session, timeout=args.timeout, limit=args.max)
        )
        if len(urls) >= args.max:
            break

    # 3) fallback if still empty
    if not urls:
        guesses = ["/", "/sitemap.xml", "/robots.txt", "/api/health"]
        urls = [urljoin(base, g.lstrip("/")) for g in guesses]

    # de-dupe, cap
    seen, uniq = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    urls = uniq[: args.max]

    # 4) crawl
    results: List[Tuple[str, int, str, str, str, bool]] = []
    do_seo = (not args.no_seo) and bool(BeautifulSoup)

    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as ex:
        futures = []
        for u in urls:
            futures.append(ex.submit(fetch_url, session, u, do_seo, args.timeout))
            if args.sleep:
                time.sleep(args.sleep)  # throttle submissions a bit if asked
        for fut in as_completed(futures):
            results.append(fut.result())

    # sort by status (failures first), then url
    results.sort(key=lambda t: (0 if (200 <= t[1] < 400) else 1, t[0]))

    # 5) write CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "status", "error", "title", "description", "is_html"])
        for row in results:
            w.writerow(row)

    # 6) stats & MD report
    ok = sum(1 for _, code, *_ in results if 200 <= code < 400)
    bad = len(results) - ok
    missing_title = sum(
        1
        for _, code, _, title, _, is_html in results
        if (200 <= code < 400) and is_html and not title.strip()
    )
    missing_desc = sum(
        1
        for _, code, _, _, desc, is_html in results
        if (200 <= code < 400) and is_html and not desc.strip()
    )

    lines: List[str] = []
    lines.append(f"# Crawl Report: {args.base_url} ({args.label})")
    lines.append(f"- Timestamp: {ts}")
    lines.append(f"- User-Agent: {ua}")
    lines.append(
        f"- Concurrency: {args.concurrency}, Retries: {args.retries}, Timeout: {args.timeout}s"
    )
    lines.append(
        f"- SEO lint: {'enabled' if do_seo else 'disabled'} (install beautifulsoup4 to enable)"
    )
    lines.append("")
    lines.append("## Discovered Sitemaps")
    if sitemaps:
        for s in sitemaps:
            lines.append(f"- {s}")
    else:
        lines.append("- *(none)*")
    lines.append("")
    lines.append(f"## Summary")
    lines.append(f"- Total URLs: {len(results)}")
    lines.append(f"- OK (2xx/3xx): {ok}")
    lines.append(f"- FAIL (other): {bad}")
    if do_seo:
        lines.append(f"- Missing <title> (HTML only): {missing_title}")
        lines.append(f"- Missing meta description (HTML only): {missing_desc}")
    lines.append(f"- CSV: `{os.path.relpath(csv_path)}`")
    lines.append("")
    lines.append("## URLs")
    for url, code, err, title, desc, is_html in results:
        status_icon = "✅" if 200 <= code < 400 else "❌"
        base_line = f"- {status_icon} {code or 'ERR'}  {url}"
        if do_seo and is_html and title:
            base_line += f"  —  **{title}**"
        if err:
            base_line += f"  ({err})"
        lines.append(base_line)
        if do_seo and is_html and desc:
            lines.append(f"  - meta: {desc}")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Saved crawl report:\n - {md_path}\n - {csv_path}")

    # 7) Optional CI gates
    exit_code = 0
    if args.fail_on_error and bad > 0:
        exit_code = 1
    if do_seo and args.require_title and missing_title > 0:
        exit_code = 1
    if do_seo and args.require_description and missing_desc > 0:
        exit_code = 1
    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        import requests  # ensure present
    except Exception:
        sys.stderr.write("This script needs 'requests'. Try: pip install requests\n")
        sys.exit(2)
    main()
