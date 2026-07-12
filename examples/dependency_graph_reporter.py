#!/usr/bin/env python3
"""
dependency_graph_reporter.py
----------------------------
Jarvis Hermes Core — Examples

Reads a simple module dependency definition (built-in sample data or a
user-supplied JSON file) and produces two outputs:

  1. A structured JSON report of the dependency graph.
  2. A Mermaid.js-compatible "graph TD" diagram that can be embedded
     directly in any Markdown file (GitHub renders it automatically).

Usage:
  python3 dependency_graph_reporter.py                  # use built-in sample
  python3 dependency_graph_reporter.py modules.json     # use custom file

Custom JSON format (array of module objects):
  [
    {"name": "ModuleA", "depends_on": ["ModuleB", "ModuleC"]},
    {"name": "ModuleB", "depends_on": []},
    {"name": "ModuleC", "depends_on": ["ModuleB"]}
  ]

No external libraries required. No network calls. No file writes (stdout only).
"""

import json
import sys
from collections import defaultdict, deque


# ---------------------------------------------------------------------------
# Built-in sample: a minimal Jarvis-like module graph
# ---------------------------------------------------------------------------
SAMPLE_MODULES = [
    {"name": "CoreBus",        "depends_on": []},
    {"name": "ConfigLoader",   "depends_on": ["CoreBus"]},
    {"name": "SecretsVault",   "depends_on": ["CoreBus"]},
    {"name": "MemoryStore",    "depends_on": ["CoreBus", "ConfigLoader"]},
    {"name": "SkillRouter",    "depends_on": ["CoreBus", "ConfigLoader"]},
    {"name": "InputListener",  "depends_on": ["CoreBus"]},
    {"name": "NLUEngine",      "depends_on": ["SkillRouter", "MemoryStore"]},
    {"name": "ActionExecutor", "depends_on": ["NLUEngine", "SecretsVault"]},
    {"name": "OutputFormatter","depends_on": ["NLUEngine"]},
    {"name": "AuditLogger",    "depends_on": ["CoreBus", "MemoryStore"]},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sanitize_name(name: str) -> str:
    """Remove characters that could break Mermaid syntax."""
    return name.replace("<", "").replace(">", "").replace('"', "").replace("'", "")


def load_modules(path: str | None) -> list[dict]:
    """Load module definitions from a JSON file or return built-in sample."""
    if path is None:
        return SAMPLE_MODULES

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, list):
        raise ValueError("JSON root must be a list of module objects.")

    for item in data:
        if "name" not in item:
            raise ValueError(f"Each module must have a 'name' field: {item}")
        if "depends_on" not in item:
            item["depends_on"] = []
        # Safety: reject path-traversal-style names
        if ".." in item["name"] or "/" in item["name"]:
            raise ValueError(f"Invalid module name (path characters not allowed): {item['name']}")

    return data


def build_graph(modules: list[dict]) -> dict:
    """
    Build adjacency structures from module list.

    Returns a dict with:
      - nodes: list of module names
      - edges: list of (from, to) dependency pairs
      - reverse_edges: dict mapping each module to its dependents
      - in_degree: how many modules each module depends on
    """
    names = {m["name"] for m in modules}
    edges = []
    reverse_edges = defaultdict(list)
    in_degree = {m["name"]: 0 for m in modules}

    for module in modules:
        src = module["name"]
        for dep in module["depends_on"]:
            if dep not in names:
                # Unknown dependency — record as warning, still include edge
                pass
            edges.append({"from": src, "to": dep})
            reverse_edges[dep].append(src)
            in_degree[src] += 1

    return {
        "nodes": sorted(names),
        "edges": edges,
        "reverse_edges": dict(reverse_edges),
        "in_degree": in_degree,
    }


def topological_order(modules: list[dict], graph: dict) -> list[str]:
    """
    Return modules in topological order (roots first) using Kahn's algorithm.
    If a cycle is detected, the remaining nodes are appended with a warning.
    """
    in_deg = dict(graph["in_degree"])  # copy
    queue = deque(sorted(n for n, d in in_deg.items() if d == 0))
    order = []

    # Build adjacency from edges (module -> its dependencies; we need dependents)
    # reverse_edges: dep -> [modules that depend on dep]
    rev = defaultdict(list, graph["reverse_edges"])

    while queue:
        node = queue.popleft()
        order.append(node)
        for dependent in sorted(rev.get(node, [])):
            in_deg[dependent] -= 1
            if in_deg[dependent] == 0:
                queue.append(dependent)

    remaining = [n for n in graph["nodes"] if n not in order]
    if remaining:
        order.extend(remaining)  # cycle — append as-is

    return order


def build_json_report(modules: list[dict], graph: dict, topo: list[str]) -> dict:
    """Assemble the structured JSON report."""
    # Compute depth (longest path from a root)
    depth_map: dict[str, int] = {}
    for name in topo:
        module = next(m for m in modules if m["name"] == name)
        if not module["depends_on"]:
            depth_map[name] = 0
        else:
            depth_map[name] = max(depth_map.get(d, 0) for d in module["depends_on"]) + 1

    nodes_detail = []
    for name in topo:
        module = next(m for m in modules if m["name"] == name)
        nodes_detail.append({
            "name": name,
            "depends_on": sorted(module["depends_on"]),
            "required_by": sorted(graph["reverse_edges"].get(name, [])),
            "depth": depth_map.get(name, 0),
        })

    root_nodes = [n["name"] for n in nodes_detail if not n["depends_on"]]
    leaf_nodes = [n["name"] for n in nodes_detail if not n["required_by"]]

    return {
        "summary": {
            "total_modules": len(modules),
            "total_edges": len(graph["edges"]),
            "root_modules": root_nodes,
            "leaf_modules": leaf_nodes,
            "max_depth": max(depth_map.values()) if depth_map else 0,
        },
        "topological_order": topo,
        "modules": nodes_detail,
    }


def build_mermaid(modules: list[dict], graph: dict) -> str:
    """Generate a Mermaid.js graph TD diagram."""
    lines = ["```mermaid", "graph TD"]

    # Node labels
    for module in modules:
        safe = _sanitize_name(module["name"])
        lines.append(f'    {safe}["{safe}"]')

    lines.append("")

    # Edges: dependency direction = depender --> dependency
    for edge in graph["edges"]:
        frm = _sanitize_name(edge["from"])
        to  = _sanitize_name(edge["to"])
        lines.append(f"    {frm} --> {to}")

    lines.append("```")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        modules = load_modules(path)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    graph = build_graph(modules)
    topo  = topological_order(modules, graph)
    report = build_json_report(modules, graph, topo)

    # --- Output 1: JSON report ---
    print("=" * 60)
    print("DEPENDENCY GRAPH REPORT (JSON)")
    print("=" * 60)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # --- Output 2: Mermaid diagram ---
    print()
    print("=" * 60)
    print("MERMAID DIAGRAM (embed in Markdown)")
    print("=" * 60)
    print(build_mermaid(modules, graph))


if __name__ == "__main__":
    main()
