"""
session_timeline_formatter.py
─────────────────────────────
Converts a list of structured event-log dictionaries into a human-readable
timeline string.  No secrets, no API keys, no personal data required.

Usage (standalone):
    python3 examples/session_timeline_formatter.py

Input schema (each event):
    {
        "timestamp": "2026-09-02T08:00:00",   # ISO-8601
        "module":    "planner",                # str
        "event":     "task_created",           # str
        "level":     "INFO",                   # INFO | WARN | ERROR
        "detail":    "..."                     # optional human note
    }

Output (stdout):
    [2026-09-02 08:00:00] [planner      ] [INFO ] task_created
                          → ...
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

# ── ANSI colour helpers (gracefully degrade if terminal doesn't support them) ──
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_CYAN   = "\033[36m"
_YELLOW = "\033[33m"
_RED    = "\033[31m"
_GREEN  = "\033[32m"
_GREY   = "\033[90m"

_LEVEL_COLOUR: dict[str, str] = {
    "INFO":  _GREEN,
    "WARN":  _YELLOW,
    "ERROR": _RED,
}

# ── Core formatter ──────────────────────────────────────────────────────────────

def _fmt_timestamp(raw: str) -> str:
    """Normalise ISO-8601 to 'YYYY-MM-DD HH:MM:SS'.  Returns raw string on error."""
    try:
        dt = datetime.fromisoformat(raw)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return str(raw)


def _level_str(level: str) -> str:
    level = (level or "INFO").upper()
    colour = _LEVEL_COLOUR.get(level, "")
    return f"{colour}{level:<5}{_RESET}"


def format_timeline(
    events: list[dict[str, Any]],
    *,
    filter_level: str | None = None,
    colour: bool = True,
) -> str:
    """
    Format a list of event dicts into a timeline string.

    Args:
        events:       List of event dictionaries.
        filter_level: If set, only include events at this level (e.g. 'ERROR').
        colour:       Emit ANSI colour codes (default True).

    Returns:
        Multi-line string ready for print() or logging.
    """
    if not colour:
        global _RESET, _BOLD, _CYAN, _YELLOW, _RED, _GREEN, _GREY
        _RESET = _BOLD = _CYAN = _YELLOW = _RED = _GREEN = _GREY = ""

    lines: list[str] = []
    target_level = (filter_level or "").upper() or None

    # Sort by timestamp string (ISO order is lexicographic-safe)
    sorted_events = sorted(events, key=lambda e: str(e.get("timestamp", "")))

    for ev in sorted_events:
        level = (ev.get("level") or "INFO").upper()
        if target_level and level != target_level:
            continue

        ts_str  = _fmt_timestamp(ev.get("timestamp", ""))
        module  = (ev.get("module")  or "unknown")[:12].ljust(12)
        event   = ev.get("event")    or "—"
        detail  = ev.get("detail")   or ""

        line = (
            f"[{_CYAN}{ts_str}{_RESET}] "
            f"[{_BOLD}{module}{_RESET}] "
            f"[{_level_str(level)}] "
            f"{event}"
        )
        lines.append(line)
        if detail:
            lines.append(f"  {_GREY}→ {detail}{_RESET}")

    if not lines:
        return f"{_YELLOW}(no events to display){_RESET}"

    header = (
        f"{_BOLD}── Session Timeline "
        f"({len(sorted_events)} events"
        f"{', filter='+target_level if target_level else ''}) ──{_RESET}"
    )
    return "\n".join([header] + lines)


def summarise(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a plain-dict summary: counts by module, counts by level, time span."""
    if not events:
        return {"total": 0, "modules": {}, "levels": {}, "span_seconds": None}

    by_module: dict[str, int] = {}
    by_level:  dict[str, int] = {}
    timestamps: list[datetime] = []

    for ev in events:
        mod = ev.get("module") or "unknown"
        lvl = (ev.get("level") or "INFO").upper()
        by_module[mod] = by_module.get(mod, 0) + 1
        by_level[lvl]  = by_level.get(lvl, 0) + 1
        try:
            timestamps.append(datetime.fromisoformat(str(ev.get("timestamp", ""))))
        except (ValueError, TypeError):
            pass

    span = None
    if len(timestamps) >= 2:
        span = round((max(timestamps) - min(timestamps)).total_seconds(), 1)

    return {
        "total":         len(events),
        "modules":       by_module,
        "levels":        by_level,
        "span_seconds":  span,
    }


# ── Demo ────────────────────────────────────────────────────────────────────────

SAMPLE_EVENTS: list[dict[str, Any]] = [
    {
        "timestamp": "2026-09-02T08:00:00",
        "module":    "planner",
        "event":     "session_start",
        "level":     "INFO",
        "detail":    "New task queue loaded (3 tasks).",
    },
    {
        "timestamp": "2026-09-02T08:00:01",
        "module":    "tool_router",
        "event":     "tool_resolved",
        "level":     "INFO",
        "detail":    "web_search → openrouter backend",
    },
    {
        "timestamp": "2026-09-02T08:00:05",
        "module":    "memory",
        "event":     "recall_hit",
        "level":     "INFO",
        "detail":    "Matched 2 relevant memory entries.",
    },
    {
        "timestamp": "2026-09-02T08:00:08",
        "module":    "tool_router",
        "event":     "rate_limit_warn",
        "level":     "WARN",
        "detail":    "Backend throttled; retrying in 1 s.",
    },
    {
        "timestamp": "2026-09-02T08:00:15",
        "module":    "planner",
        "event":     "task_completed",
        "level":     "INFO",
        "detail":    "All 3 tasks processed.",
    },
    {
        "timestamp": "2026-09-02T08:00:16",
        "module":    "session",
        "event":     "session_end",
        "level":     "INFO",
    },
]


def main() -> None:
    print(format_timeline(SAMPLE_EVENTS))
    print()
    summary = summarise(SAMPLE_EVENTS)
    print(f"{_BOLD}── Summary ──{_RESET}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
