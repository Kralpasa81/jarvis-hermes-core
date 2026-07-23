#!/usr/bin/env python3
"""Check that Jarvis / Hermes daily lab notes contain their expected sections.

This is the module proposed in the 2026-07-22 daily note
(`daily_note_health_check`). It is **not** a real CI job -- it is a small,
dependency-free static check that reads Markdown files under `docs/daily/`
and reports, per note, whether each of the five expected sections (focus,
architecture note, actionable task, future module idea, security reminder)
appears to be present. Detection is keyword-based and intentionally forgiving
because the daily notes in this repo have used a few different header styles
and languages (English/Turkish) over time.

Safety rules enforced by this tool:
  - It only reads Markdown files under `docs/daily/` (or a caller-supplied
    relative directory) -- no private files, no environment variables, no
    network calls.
  - It never modifies a daily note; it only reports missing-section
    warnings.
  - `--daily-dir` and `--output` only accept relative paths with no ".."
    segments (no path traversal, no absolute paths).
  - Output never echoes full note bodies -- only filenames, per-section
    presence flags, and a short status label (`ok` / `missing-sections`).

Usage:
  python3 examples/daily_note_health_check.py                  # markdown report
  python3 examples/daily_note_health_check.py --format json
  python3 examples/daily_note_health_check.py --strict          # exit 1 if any note is missing sections
  python3 examples/daily_note_health_check.py --daily-dir docs/daily --output out.md
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

# Keyword groups used to detect each expected section, independent of the
# exact header wording or language used in a given note. Matching is
# case-insensitive substring search over the whole note body.
REQUIRED_SECTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("focus", ("today's focus", "kısa hedef", "short goal", "bugünün hedefi")),
    ("architecture_note", ("architecture note", "mimari not")),
    ("actionable_task", ("small task", "actionable task", "yapılabilir görev")),
    ("future_module_idea", ("future module", "future idea", "gelecekteki modül")),
    ("security_reminder", ("security", "secret", "güvenlik", "api key", "token")),
)


class DailyNoteHealthCheckError(ValueError):
    """Raised when a caller-supplied path breaks the safety contract."""


@dataclass(frozen=True)
class NoteResult:
    file: str
    present: tuple[str, ...]
    missing: tuple[str, ...]
    status: str  # "ok" | "missing-sections"


def _safe_relative_dir(raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise DailyNoteHealthCheckError(
            "--daily-dir must be a relative path with no '..' segments"
        )
    return path


def _safe_output_path(raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise DailyNoteHealthCheckError(
            "--output must be a relative path with no '..' segments"
        )
    return path


def check_note(path: Path) -> NoteResult:
    text = path.read_text(encoding="utf-8", errors="replace").lower()

    present = []
    missing = []
    for section_name, keywords in REQUIRED_SECTIONS:
        if any(keyword in text for keyword in keywords):
            present.append(section_name)
        else:
            missing.append(section_name)

    status = "ok" if not missing else "missing-sections"
    return NoteResult(file=path.name, present=tuple(present), missing=tuple(missing), status=status)


def run_health_check(daily_dir: Path) -> list[NoteResult]:
    if not daily_dir.is_dir():
        raise DailyNoteHealthCheckError(f"daily notes directory not found: {daily_dir}")

    md_files = sorted(daily_dir.glob("*.md"))
    return [check_note(path) for path in md_files]


def to_markdown(results: list[NoteResult]) -> str:
    if not results:
        return "# Daily Note Health Check\n\nNo daily notes found."

    ok_count = sum(1 for r in results if r.status == "ok")
    warn_count = len(results) - ok_count

    lines = [
        "# Daily Note Health Check",
        "",
        "Keyword-based section-presence check only. This does not judge the",
        "quality of a note's content, only whether each expected section",
        "appears to be present somewhere in the file.",
        "",
        f"- Notes checked: {len(results)}",
        f"- 🟢 `ok`: {ok_count}",
        f"- 🟡 `missing-sections`: {warn_count}",
        "",
        "| Note | Status | Missing sections |",
        "| --- | --- | --- |",
    ]
    for r in results:
        missing_label = ", ".join(f"`{m}`" for m in r.missing) if r.missing else "-"
        icon = "🟢" if r.status == "ok" else "🟡"
        lines.append(f"| `{r.file}` | {icon} {r.status} | {missing_label} |")
    return "\n".join(lines)


def to_json(results: list[NoteResult]) -> str:
    return json.dumps([asdict(r) for r in results], indent=2, sort_keys=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check docs/daily/*.md notes for expected section keywords."
    )
    parser.add_argument(
        "--daily-dir",
        default="docs/daily",
        help="Relative path to the daily notes directory (default: docs/daily).",
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument(
        "--output",
        help="Optional relative file path to also write the rendered output to (no '..' allowed).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 if any note is missing a section (default: exit 0 either way).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        daily_dir = _safe_relative_dir(args.daily_dir)
        results = run_health_check(daily_dir)
    except DailyNoteHealthCheckError as exc:
        print(f"daily_note_health_check_error: {exc}")
        return 2

    rendered = to_json(results) if args.format == "json" else to_markdown(results)
    print(rendered)

    if args.output:
        try:
            out_path = _safe_output_path(args.output)
        except DailyNoteHealthCheckError as exc:
            print(f"daily_note_health_check_error: {exc}")
            return 2
        out_path.write_text(rendered + "\n", encoding="utf-8")

    if args.strict and any(r.status != "ok" for r in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
