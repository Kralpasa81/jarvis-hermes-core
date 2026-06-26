#!/usr/bin/env python3
"""Public-safe repository safety scanner for Jarvis / Hermes examples.

The scanner looks for high-signal patterns that should not appear in a public
repo: token-like literals, private-key blocks, credential assignments, private
network URLs, and accidental .env files. It does not contact any service and it
prints only file paths, line numbers, and rule names -- never the matched value.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

TEXT_EXTENSIONS = {
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".text",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

SKIP_DIRS = {".git", ".hg", ".mypy_cache", ".pytest_cache", ".ruff_cache", "__pycache__", "node_modules", "venv", ".venv"}
ENV_FILE_NAMES = {".env", ".env.local", ".env.production", "secrets.json", "credentials.json"}

RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-key-block", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("openai-style-token", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("credential-assignment", re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=:-]{12,}")),
    ("private-network-url", re.compile(r"https?://(?:10\.|127\.|192\.168\.|172\.(?:1[6-9]|2\d|3[0-1])\.)\d{1,3}(?:\.\d{1,3}){2}(?::\d+)?")),
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str


def iter_candidate_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and (path.suffix.lower() in TEXT_EXTENSIONS or path.name in ENV_FILE_NAMES):
            yield path


def scan_file(path: Path, root: Path) -> list[Finding]:
    relative = path.relative_to(root).as_posix()
    findings: list[Finding] = []

    if path.name in ENV_FILE_NAMES:
        findings.append(Finding(relative, 1, "sensitive-filename"))

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return findings

    for line_number, line in enumerate(lines, start=1):
        for rule_name, pattern in RULES:
            if pattern.search(line):
                findings.append(Finding(relative, line_number, rule_name))
    return findings


def scan(root: Path) -> list[Finding]:
    return [finding for path in iter_candidate_files(root) for finding in scan_file(path, root)]


def render_markdown(findings: list[Finding]) -> str:
    if not findings:
        return "# Public Safety Scan\n\nNo high-signal public-safety findings were detected."

    rows = ["# Public Safety Scan", "", "| Path | Line | Rule |", "| --- | ---: | --- |"]
    rows.extend(f"| `{item.path}` | {item.line} | `{item.rule}` |" for item in findings)
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a repo for public-safety risk patterns without printing secret values.")
    parser.add_argument("root", nargs="?", default=".", help="Directory to scan; defaults to the current directory.")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown", help="Output format.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings = scan(root)

    if args.format == "json":
        print(json.dumps({"root": str(root), "finding_count": len(findings), "findings": [asdict(item) for item in findings]}, indent=2))
    else:
        print(render_markdown(findings))

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
