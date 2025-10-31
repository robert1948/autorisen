#!/usr/bin/env python3
"""
Figma exporter: reads a CSV manifest of frames and downloads PNG/SVG/PDF
via Figma Images API, saving to docs and client asset paths.

CSV columns (header required):
name,node_id,format,scale,docs_path,client_path

- format: png|svg|pdf
- scale: 1..4 (for PNG), ignored for SVG/PDF
- docs_path/client_path: relative subpaths; may be empty

Requires:
  --token <FIGMA_TOKEN>
  --file-id <FIGMA_FILE_ID>
  --csv docs/figma/frames.csv
"""
import argparse, csv, json, os, sys, time, urllib.request, urllib.parse

API_BASE = "https://api.figma.com/v1"


def http_get(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        return r.read()


def ensure_dir(p):
    if p and not os.path.isdir(p):
        os.makedirs(p, exist_ok=True)


def save_bytes(path, content):
    ensure_dir(os.path.dirname(path))
    with open(path, "wb") as f:
        f.write(content)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True)
    ap.add_argument("--file-id", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out-docs", required=True)
    ap.add_argument("--out-client", required=True)
    args = ap.parse_args()

    headers = {"X-Figma-Token": args.token}

    rows = []
    with open(args.csv, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            if not row.get("node_id"):
                print(f"skip row {i}: missing node_id", file=sys.stderr)
                continue
            rows.append(row)

    # Group nodes by format/scale to minimize API calls
    groups = {}
    for r in rows:
        fmt = (r.get("format") or "png").lower()
        scale = r.get("scale") or ("1" if fmt == "png" else "")
        key = (fmt, scale)
        groups.setdefault(key, []).append(r["node_id"])

    # Hit Figma Images API per group
    images_urls = {}  # node_id -> download URL
    for (fmt, scale), node_ids in groups.items():
        params = {
            "ids": ",".join(node_ids),
            "format": fmt,
        }
        if fmt == "png" and scale:
            params["scale"] = scale
        url = f"{API_BASE}/images/{args.file_id}?{urllib.parse.urlencode(params)}"
        data = json.loads(http_get(url, headers))
        err = data.get("err")
        if err:
            print(f"Figma API error: {err}", file=sys.stderr)
            sys.exit(2)
        images = data.get("images", {})
        images_urls.update(images)

    # Download and write to docs/client paths
    for r in rows:
        node_id = r["node_id"]
        name = (r.get("name") or node_id).strip().replace(" ", "_")
        fmt = (r.get("format") or "png").lower()
        docs_rel = (r.get("docs_path") or "").strip()
        client_rel = (r.get("client_path") or "").strip()

        dl = images_urls.get(node_id)
        if not dl:
            print(f"warning: no image URL for node {node_id}", file=sys.stderr)
            continue

        content = http_get(dl, headers={})
        # docs output
        if docs_rel != "":
            out_docs = os.path.join(args.out_docs, docs_rel, f"{name}.{fmt}")
        else:
            out_docs = os.path.join(args.out_docs, f"{name}.{fmt}")
        save_bytes(out_docs, content)

        # client output
        if client_rel != "":
            out_client = os.path.join(args.out_client, client_rel, f"{name}.{fmt}")
        else:
            out_client = os.path.join(args.out_client, f"{name}.{fmt}")
        save_bytes(out_client, content)

        time.sleep(0.05)  # be polite
        print(f"exported {name}.{fmt}")


if __name__ == "__main__":
    main()
