#!/usr/bin/env python3
"""Preview rough keyword overlap between docs/roadmap.md phases and daily notes.

This is the module proposed in the 2026-07-24 daily note
(`roadmap_phase_tracker`). It is **not** a real project-management tool and
it does **not** decide whether a roadmap item is actually done. It is a
small, dependency-free, read-only preview that:

  1. Reads `docs/roadmap.md` and splits it into "Phase N" sections, each with
     its list of bullet items (plain Markdown "- ..." lines).
  2. Reads every `docs/daily/*.md` note and collects the text of completed
     checklist items (lines shaped like ``- [x] ...`` or ``- [X] ...``).
  3. For each roadmap bullet, does a coarse, case-insensitive keyword-overlap
     check against the completed-task text (words of 4+ letters, common stop
     words removed). If any significant word overlaps, the bullet is marked
     `possible-overlap` and the matching note date(s) are listed; otherwise
     it is marked `no-daily-mention`.

This is intentionally shallow: keyword overlap is not proof of completion,
just a rough pointer for a human to look closer at. The tool never marks a
roadmap bullet as "done" and never edits `docs/roadmap.md` or any daily note.

Safety rules enforced by this tool:
  - It only reads `docs/roadmap.md` and `docs/daily/*.md` (or a caller
    supplied relative repo root) -- no environment variables, no network
    calls, no writes other than an optional explicit `--output` file.
  - It never modifies `docs/roadmap.md` or any daily note.
  - `--repo-root` and `--output` only accept relative paths with no ".."
    segments (no path traversal, no absolute paths).
  - Output only shows roadmap bullet text (already public) and daily-note
    filenames -- no private data, no secrets, no personal identifiers.

Usage:
  python3 examples/roadmap_phase_tracker.py                     # markdown report
  python3 examples/roadmap_phase_tracker.py --format json
  python3 examples/roadmap_phase_tracker.py --repo-root . --output out.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PHASE_HEADER_RE = re.compile(r"^##\s+(Phase\s+\d+.*)$")
BULLET_RE = re.compile(r"^-\s+(.*\S)\s*$")
DONE_CHECKBOX_RE = re.compile(r"^\s*-\s*\[[xX]\]\s*(.*\S)\s*$")

STOPWORDS = {
    "with", "from", "that", "this", "into", "your", "have", "which",
    "should", "where", "when", "such", "each", "will", "than", "does",
    "only", "over", "avoid", "keep", "add", "the", "and", "for", "all",
}


def reject_unsafe_path(raw: str, *, label: str) -> Path:
    if raw.startswith("/") or ".." in Path(raw).parts:
        raise SystemExit(
            f"Refusing unsafe {label} path: {raw!r} "
            "(absolute paths and '..' segments are not allowed)"
        )
    return Path(raw)


def significant_words(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z]{4,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


def parse_roadmap_phases(roadmap_path: Path) -> list[dict]:
    if not roadmap_path.is_file():
        return []

    phases: list[dict] = []
    current = None
    for raw_line in roadmap_path.read_text(encoding="utf-8").splitlines():
        header_match = PHASE_HEADER_RE.match(raw_line.strip())
        if header_match:
            current = {"phase": header_match.group(1).strip(), "bullets": []}
            phases.append(current)
            continue
        if current is None:
            continue
        bullet_match = BULLET_RE.match(raw_line)
        if bullet_match:
            current["bullets"].append(bullet_match.group(1).strip())
    return phases


def collect_completed_tasks(daily_dir: Path) -> list[dict]:
    if not daily_dir.is_dir():
        return []

    tasks = []
    for note_path in sorted(daily_dir.glob("*.md")):
        for raw_line in note_path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = DONE_CHECKBOX_RE.match(raw_line)
            if match:
                tasks.append({"note": note_path.stem, "text": match.group(1).strip()})
    return tasks


def build_report(repo_root: Path) -> dict:
    roadmap_path = repo_root / "docs" / "roadmap.md"
    daily_dir = repo_root / "docs" / "daily"

    phases = parse_roadmap_phases(roadmap_path)
    tasks = collect_completed_tasks(daily_dir)
    task_words = [(t["note"], significant_words(t["text"])) for t in tasks]

    report_phases = []
    total_bullets = 0
    overlap_bullets = 0

    for phase in phases:
        rows = []
        for bullet in phase["bullets"]:
            total_bullets += 1
            bullet_words = significant_words(bullet)
            matching_notes = sorted(
                {note for note, words in task_words if bullet_words & words}
            )
            status = "possible-overlap" if matching_notes else "no-daily-mention"
            if matching_notes:
                overlap_bullets += 1
            rows.append(
                {
                    "bullet": bullet,
                    "status": status,
                    "matching_notes": matching_notes[:5],
                    "matching_notes_truncated": len(matching_notes) > 5,
                }
            )
        report_phases.append({"phase": phase["phase"], "rows": rows})

    return {
        "phases_found": len(phases),
        "daily_notes_scanned": len({t["note"] for t in tasks}),
        "completed_tasks_scanned": len(tasks),
        "bullets_total": total_bullets,
        "bullets_with_possible_overlap": overlap_bullets,
        "phases": report_phases,
    }


def render_markdown(report: dict) -> str:
    lines = ["# Roadmap Phase Overlap Preview", ""]
    lines.append(
        "Rough keyword-overlap preview only -- **not** a real completion "
        "tracker. `possible-overlap` means a roadmap bullet shares a "
        "significant word with at least one completed daily-note checklist "
        "item; it does not mean the roadmap item is actually finished."
    )
    lines.append("")
    lines.append(
        f"Scanned {report['phases_found']} phase(s), "
        f"{report['bullets_total']} bullet(s), "
        f"{report['daily_notes_scanned']} daily note(s), "
        f"{report['completed_tasks_scanned']} completed checklist item(s). "
        f"{report['bullets_with_possible_overlap']} bullet(s) show possible overlap."
    )
    lines.append("")

    for phase in report["phases"]:
        lines.append(f"## {phase['phase']}")
        lines.append("")
        lines.append("| bullet | status | matching notes |")
        lines.append("| --- | --- | --- |")
        for row in phase["rows"]:
            notes = ", ".join(row["matching_notes"]) if row["matching_notes"] else "-"
            if row["matching_notes_truncated"]:
                notes += ", ..."
            lines.append(f"| {row['bullet']} | {row['status']} | {notes} |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Relative path to the repo root (default: current directory).",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional relative output file path (no '..' segments allowed).",
    )
    args = parser.parse_args()

    repo_root = reject_unsafe_path(args.repo_root, label="--repo-root")
    report = build_report(repo_root)

    if args.format == "json":
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    else:
        rendered = render_markdown(report)

    if args.output:
        output_path = reject_unsafe_path(args.output, label="--output")
        output_path.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
