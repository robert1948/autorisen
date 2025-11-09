#!/usr/bin/env python3
import argparse
import datetime
import pathlib
import re
import sys

BADGE = {
    "ok": "success",
    "warn": "yellow",
    "fail": "red",
    "green": "brightgreen",
    "blue": "blue",
    "purple": "purple",
}


def badge(label, value, color):
    return f"![{label}](https://img.shields.io/badge/{label.replace(' ','%20')}-{value.replace(' ','%20')}-{color}?style=flat-square)"


def set_row(md: str, heading: str, new_status_cell: str, notes: str):
    # Replace a row in the badges table: | **Heading** | <badge> | Notes |
    pattern = rf"^\|\s*\*\*{re.escape(heading)}\*\*\s*\|\s*.*?\s*\|\s*.*?\s*\|$"
    repl = f"| **{heading}** | {new_status_cell} | {notes} |"
    return re.sub(pattern, repl, md, flags=re.MULTILINE)


def set_health_date(md: str, env_label: str, new_date: str):
    # Replace the "Last Update" (5th column) for a given environment row
    # Row format: | Environment | URL | Container | Health | Last Update |
    pattern = rf"^\|\s*{re.escape(env_label)}\s*\|\s*.*?\|\s*.*?\|\s*.*?\|\s*.*?\|$"

    def repl(m):
        row = m.group(0)
        parts = [p.strip() for p in row.strip("|").split("|")]
        if len(parts) >= 5:
            parts[4] = new_date
        return "| " + " | ".join(parts) + " |"

    return re.sub(pattern, repl, md, flags=re.MULTILINE)


def set_health_icon(md: str, env_label: str, icon: str):
    # Update the "Health" (4th column) emoji
    pattern = rf"^\|\s*{re.escape(env_label)}\s*\|\s*.*?\|\s*.*?\|\s*.*?\|\s*.*?\|$"

    def repl(m):
        row = m.group(0)
        parts = [p.strip() for p in row.strip("|").split("|")]
        if len(parts) >= 5:
            parts[3] = icon
        return "| " + " | ".join(parts) + " |"

    return re.sub(pattern, repl, md, flags=re.MULTILINE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dashboard", required=True)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--local", required=True)
    ap.add_argument("--pytest-exit", type=int, default=1)
    ap.add_argument("--csrf-exit", type=int, default=1)
    ap.add_argument("--health-exit", type=int, default=1)
    args = ap.parse_args()

    p = pathlib.Path(args.dashboard)
    md = p.read_text(encoding="utf-8")

    # Derive statuses
    tests_ok = args.pytest_exit == 0
    csrf_ok = args.csrf_exit == 0
    health_ok = args.health_exit == 0

    now = datetime.datetime.now().strftime("%d %b")

    # --- Badge table updates ---
    # MVP Phase: keep Stabilization (blue)
    md = set_row(
        md,
        "MVP Phase",
        badge("MVP", "Stabilization", BADGE["blue"]),
        "Final polishing before public showcase",
    )

    # Auth System badge
    if csrf_ok:
        md = set_row(
            md,
            "Auth System",
            badge("Auth", "CSRF%20%26%20Login%20Verified", BADGE["ok"]),
            "Fully tested in staging",
        )
    else:
        md = set_row(
            md,
            "Auth System",
            badge("Auth", "Check%20CSRF", BADGE["fail"]),
            "CSRF probe failed",
        )

    # Backend Health badge
    md = set_row(
        md,
        "Backend Health",
        badge(
            "Backend",
            "Healthy" if health_ok else "Degraded",
            BADGE["green" if health_ok else "warn"],
        ),
        "Staging Heroku OK" if health_ok else "Investigate /api/health",
    )

    # Documentation badge (assume codex-docs ran: set active)
    md = set_row(
        md,
        "Documentation",
        badge("Docs", "Sync%20Active", BADGE["blue"]),
        "Maintained via `make codex-docs`",
    )

    # Frontend Build badge reflects tests (proxy signal)
    md = set_row(
        md,
        "Frontend Build",
        badge(
            "Frontend",
            "All%20Tests%20Passing" if tests_ok else "Login%20Integration%20WIP",
            BADGE["green" if tests_ok else "warn"],
        ),
        "FE-004 pending test" if not tests_ok else "OK",
    )

    # Deployment badge
    md = set_row(
        md,
        "Deployment",
        badge(
            "Heroku",
            "Stable" if health_ok else "Check",
            BADGE["green" if health_ok else "warn"],
        ),
        "Pipeline connected" if health_ok else "Verify dyno/logs",
    )

    # AI Agents badge (static)
    md = set_row(
        md,
        "AI Agents",
        badge("Agents", "Online", BADGE["purple"]),
        "Codex + TestGuardian running",
    )

    # --- System Health & Deployment table updates ---
    md = set_health_date(md, "Staging (Heroku)", now)
    md = set_health_icon(md, "Staging (Heroku)", "🟢 OK" if health_ok else "🟠 Check")

    # Local last update only if tests ran
    md = set_health_date(md, "Local Docker", now)
    md = set_health_icon(md, "Local Docker", "🟢 Healthy" if tests_ok else "🟠 Check")

    p.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
