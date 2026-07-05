"""
weekly_review_summary.py

Reads all Markdown daily notes from docs/daily/ and prints a summary table
showing each note's date, focus line, and whether a future-module idea was
mentioned.

No external dependencies. No API calls. No private data. Runs entirely from
the local repository tree.

Usage:
    python3 examples/weekly_review_summary.py
    python3 examples/weekly_review_summary.py --week          # current week only
    python3 examples/weekly_review_summary.py --json          # JSON output
    python3 examples/weekly_review_summary.py --week --json
"""

import argparse
import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_daily_dir() -> Path:
    """Locate docs/daily/ relative to this script or the repo root."""
    candidates = [
        Path(__file__).parent.parent / "docs" / "daily",
        Path("docs") / "daily",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    sys.exit("ERROR: docs/daily/ directory not found. Run from the repo root.")


def parse_note(path: Path) -> dict:
    """Extract key fields from a daily note Markdown file."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    focus = ""
    has_future_idea = False
    has_security_reminder = False

    # State machine: capture the first non-empty line after "## Today's focus"
    in_focus = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## today"):
            in_focus = True
            continue
        if in_focus:
            if stripped.startswith("##"):
                in_focus = False
            elif stripped:
                focus = stripped
                in_focus = False

        lower = stripped.lower()
        if "future module" in lower or "future idea" in lower:
            has_future_idea = True
        if "secret" in lower or "token" in lower or "api key" in lower:
            has_security_reminder = True

    # Derive date from filename (YYYY-MM-DD.md)
    stem = path.stem
    try:
        note_date = date.fromisoformat(stem)
    except ValueError:
        note_date = None

    return {
        "date": stem,
        "date_obj": note_date,
        "focus": focus or "(no focus line found)",
        "has_future_idea": has_future_idea,
        "has_security_reminder": has_security_reminder,
    }


def current_week_range() -> tuple[date, date]:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def print_markdown_table(notes: list[dict]) -> None:
    col_date = max(len("Date"), max(len(n["date"]) for n in notes))
    col_focus = max(len("Today's Focus"), max(len(n["focus"]) for n in notes))
    col_idea = len("Future Idea")
    col_sec = len("Sec Reminder")

    h_date = "Date"
    h_focus = "Today's Focus"
    h_idea = "Future Idea"
    h_sec = "Sec Reminder"

    header = (
        f"| {h_date:<{col_date}} "
        f"| {h_focus:<{col_focus}} "
        f"| {h_idea:<{col_idea}} "
        f"| {h_sec:<{col_sec}} |"
    )
    sep = (
        f"| {'-' * col_date} "
        f"| {'-' * col_focus} "
        f"| {'-' * col_idea} "
        f"| {'-' * col_sec} |"
    )
    print(header)
    print(sep)
    for n in notes:
        idea_flag = "✓" if n["has_future_idea"] else ""
        sec_flag = "✓" if n["has_security_reminder"] else ""
        print(
            f"| {n['date']:<{col_date}} "
            f"| {n['focus']:<{col_focus}} "
            f"| {idea_flag:<{col_idea}} "
            f"| {sec_flag:<{col_sec}} |"
        )


def print_json(notes: list[dict]) -> None:
    safe = [{k: v for k, v in n.items() if k != "date_obj"} for n in notes]
    print(json.dumps(safe, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarise Jarvis/Hermes daily lab notes from docs/daily/."
    )
    parser.add_argument(
        "--week",
        action="store_true",
        help="Show only notes from the current calendar week (Mon–Sun).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output as JSON instead of a Markdown table.",
    )
    args = parser.parse_args()

    daily_dir = find_daily_dir()
    md_files = sorted(daily_dir.glob("*.md"))

    if not md_files:
        print("No daily notes found in", daily_dir)
        return

    notes = [parse_note(f) for f in md_files]
    # Keep only parseable dates
    notes = [n for n in notes if n["date_obj"] is not None]
    notes.sort(key=lambda n: n["date_obj"])

    if args.week:
        monday, sunday = current_week_range()
        notes = [n for n in notes if monday <= n["date_obj"] <= sunday]
        if not notes:
            print(f"No notes found for the current week ({monday} – {sunday}).")
            return
        print(f"## Weekly Review: {monday} – {sunday}\n")
    else:
        print(f"## All Daily Notes ({len(notes)} total)\n")

    if args.as_json:
        print_json(notes)
    else:
        print_markdown_table(notes)

    print(f"\nTotal notes shown: {len(notes)}")
    if args.week:
        print("Tip: run without --week to see all notes.")


if __name__ == "__main__":
    main()
