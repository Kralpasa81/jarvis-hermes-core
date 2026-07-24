#!/usr/bin/env python3
"""Cross-check examples/*.py docstrings against the README "Safe Examples" table.

This is the module proposed in the 2026-07-23 daily note
(`example_catalog_indexer`). It is **not** an automatic README updater -- it
is a small, dependency-free static check that:

  1. Reads every `examples/*.py` file and extracts its module docstring
     title (the first non-empty line of the triple-quoted docstring) and
     whether it contains a `Usage:` block.
  2. Reads `README.md` and extracts the list of example filenames already
     referenced in the "Safe Examples" section (lines shaped like
     ``- [`examples/name.py`](examples/name.py) ...``).
  3. Reports, per example file, one of:
       - `ok`            -- has a docstring title, has a Usage block, and is
                             listed in the README Safe Examples table.
       - `missing-usage` -- has a docstring title but no Usage block.
       - `missing-readme`-- has a docstring title but is not referenced in
                             the README Safe Examples table.
       - `no-docstring`  -- the file has no module docstring at all.
     It also reports README entries that reference a file that no longer
     exists under `examples/` (`readme-only`), so the two lists never
     silently drift apart.

Safety rules enforced by this tool:
  - It only reads `examples/*.py` and `README.md` from the current working
    directory (or a caller-supplied relative repo root) -- no environment
    variables, no network calls, no writes to any file.
  - It never modifies `README.md` or any example file; it only reports.
  - `--repo-root` and `--output` only accept relative paths with no ".."
    segments (no path traversal, no absolute paths).
  - Output never dumps full file contents -- only filenames, short docstring
    titles (already public documentation, one line), and status labels.

Usage:
  python3 examples/example_catalog_indexer.py                    # markdown report
  python3 examples/example_catalog_indexer.py --format json
  python3 examples/example_catalog_indexer.py --strict            # exit 1 if any mismatch found
  python3 examples/example_catalog_indexer.py --repo-root . --output out.md
"""

import argparse
import json
import re
import sys
from pathlib import Path

DOCSTRING_RE = re.compile(r'^\s*"""(.*?)"""', re.DOTALL | re.MULTILINE)
README_ENTRY_RE = re.compile(
    r"-\s*\[`examples/([A-Za-z0-9_\-]+\.py)`\]\(examples/([A-Za-z0-9_\-]+\.py)\)"
)


def reject_unsafe_path(raw: str, *, label: str) -> Path:
    if raw.startswith("/") or ".." in Path(raw).parts:
        raise SystemExit(
            f"Refusing unsafe {label} path: {raw!r} "
            "(absolute paths and '..' segments are not allowed)"
        )
    return Path(raw)


def extract_docstring_title(text: str) -> str | None:
    match = DOCSTRING_RE.search(text)
    if not match:
        return None
    body = match.group(1).strip()
    if not body:
        return ""
    first_line = body.splitlines()[0].strip()
    return first_line


def has_usage_block(text: str) -> bool:
    return bool(re.search(r"^\s*Usage:\s*$", text, re.MULTILINE))


def collect_example_files(examples_dir: Path) -> list[Path]:
    if not examples_dir.is_dir():
        return []
    return sorted(
        p
        for p in examples_dir.glob("*.py")
        if p.name != "__init__.py"
    )


def collect_readme_entries(readme_path: Path) -> set[str]:
    if not readme_path.is_file():
        return set()
    text = readme_path.read_text(encoding="utf-8")
    names = set()
    for match in README_ENTRY_RE.finditer(text):
        names.add(match.group(1))
    return names


def build_report(repo_root: Path) -> dict:
    examples_dir = repo_root / "examples"
    readme_path = repo_root / "README.md"

    example_files = collect_example_files(examples_dir)
    readme_entries = collect_readme_entries(readme_path)

    rows = []
    seen_names = set()
    for path in example_files:
        name = path.name
        seen_names.add(name)
        text = path.read_text(encoding="utf-8")
        title = extract_docstring_title(text)
        in_readme = name in readme_entries

        if title is None:
            status = "no-docstring"
        elif not has_usage_block(text):
            status = "missing-usage"
        elif not in_readme:
            status = "missing-readme"
        else:
            status = "ok"

        rows.append(
            {
                "file": name,
                "docstring_title": title or "",
                "has_usage_block": has_usage_block(text) if title is not None else False,
                "in_readme_table": in_readme,
                "status": status,
            }
        )

    readme_only = sorted(readme_entries - seen_names)

    ok_count = sum(1 for r in rows if r["status"] == "ok")
    mismatch_count = len(rows) - ok_count + len(readme_only)

    return {
        "examples_checked": len(rows),
        "ok_count": ok_count,
        "mismatch_count": mismatch_count,
        "rows": rows,
        "readme_only_entries": readme_only,
    }


def render_markdown(report: dict) -> str:
    lines = ["# Example Catalog Index Report", ""]
    lines.append(
        f"Checked {report['examples_checked']} file(s) under `examples/`: "
        f"{report['ok_count']} ok, {report['mismatch_count']} mismatch(es)."
    )
    lines.append("")
    lines.append("| file | docstring title | usage block | in README table | status |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in report["rows"]:
        title = row["docstring_title"] or "(none)"
        lines.append(
            f"| `{row['file']}` | {title} | "
            f"{'yes' if row['has_usage_block'] else 'no'} | "
            f"{'yes' if row['in_readme_table'] else 'no'} | {row['status']} |"
        )

    if report["readme_only_entries"]:
        lines.append("")
        lines.append("## README entries with no matching file under `examples/`")
        for name in report["readme_only_entries"]:
            lines.append(f"- `{name}`")

    return "\n".join(lines) + "\n"


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
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 if any mismatch is found.",
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

    if args.strict and report["mismatch_count"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
