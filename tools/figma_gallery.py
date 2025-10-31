#!/usr/bin/env python3
"""
Build a Markdown gallery from exported Figma frames.

- Scans docs/figma/_export for *.png/*.svg/*.pdf
- Writes docs/figma/GALLERY.md with a clean grid preview
- Optionally copies previews into docs/img/figma for linking

No third-party deps.
"""
from pathlib import Path
import argparse
import shutil


def rel(p: Path, base: Path) -> str:
    return str(p.relative_to(base)).replace("\\", "/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-dir", default="docs/figma/_export")
    ap.add_argument("--gallery-md", default="docs/figma/GALLERY.md")
    ap.add_argument("--mirror-docs", default="docs/img/figma")  # for stable doc embeds
    args = ap.parse_args()

    export_dir = Path(args.export_dir)
    mirror_dir = Path(args.mirror_docs)
    gallery_md = Path(args.gallery_md)

    export_dir.mkdir(parents=True, exist_ok=True)
    mirror_dir.mkdir(parents=True, exist_ok=True)
    gallery_md.parent.mkdir(parents=True, exist_ok=True)

    exts = {".png", ".svg", ".pdf"}
    files = sorted(p for p in export_dir.rglob("*") if p.suffix.lower() in exts)

    # Mirror images (skip PDFs for mirror)
    mirrored = []
    for p in files:
        if p.suffix.lower() == ".pdf":
            continue
        dst = mirror_dir / rel(p, export_dir)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or p.stat().st_mtime > dst.stat().st_mtime:
            shutil.copy2(p, dst)
        mirrored.append(dst)

    # Build markdown
    lines = []
    lines.append("# 📸 Figma Gallery\n")
    lines.append("_Auto-generated from exports in `docs/figma/_export`._\n")
    lines.append("")
    if not files:
        lines.append("> No exported frames found. Run `make figma-export` first.\n")
    else:
        # Simple 3-wide grid with inline images (use docs/img/figma mirror)
        lines.append("## Frames\n")
        lines.append("")
        col = 0
        row = []
        for img in mirrored:
            # Use relative path from docs/ to keep links portable
            relpath = rel(img, Path("docs"))
            name = img.stem.replace("_", " ").title()
            cell = f'<div style="text-align:center;"><img src="../{relpath}" alt="{name}" width="360"><br/><sub>{name}</sub></div>'
            row.append(cell)
            col += 1
            if col == 3:
                lines.append(
                    f'<div style="display:flex; gap:12px;">{"".join(f"<div>{c}</div>" for c in row)}</div>\n'
                )
                row, col = [], 0
        if row:
            lines.append(
                f'<div style="display:flex; gap:12px;">{"".join(f"<div>{c}</div>" for c in row)}</div>\n'
            )

        # List PDFs at the end
        pdfs = [p for p in files if p.suffix.lower() == ".pdf"]
        if pdfs:
            lines.append("\n## PDFs\n")
            for p in pdfs:
                relpdf = rel(p, Path("docs"))
                lines.append(f"- [{p.stem}]({relpdf})")

    gallery_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {gallery_md}")


if __name__ == "__main__":
    main()
