#!/usr/bin/env python3
"""
tool_chain_flow_diagram.py
--------------------------
Jarvis-Hermes araç zincirini (tool_search → tool_describe → tool_call)
ASCII akış diyagramı olarak terminale yazdırır.

Çalıştırma: python3 examples/tool_chain_flow_diagram.py
Bağımlılık: yok (standart kütüphane yeterli)
Public-safe: token, key, kişisel veri içermez.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Step:
    name: str
    description: str
    outputs: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)


TOOL_CHAIN: List[Step] = [
    Step(
        name="tool_search",
        description="Deferred araçları anahtar kelimeyle ara",
        outputs=["araç adları listesi", "kısa açıklamalar"],
        depends_on=[],
    ),
    Step(
        name="tool_describe",
        description="Seçilen araçların tam JSON şemalarını yükle",
        outputs=["parametre şemaları", "zorunlu/opsiyonel alanlar"],
        depends_on=["tool_search"],
    ),
    Step(
        name="tool_call",
        description="Şemaya uygun argümanlarla aracı çalıştır",
        outputs=["araç sonucu", "hata varsa açıklama"],
        depends_on=["tool_describe"],
    ),
]


BOX_WIDTH = 60
H_LINE = "─" * BOX_WIDTH
CONNECTOR = "          │"
ARROW = "          ▼"


def _wrap(text: str, width: int = BOX_WIDTH - 4) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""
    for w in words:
        if len(current) + len(w) + 1 > width:
            lines.append(current.strip())
            current = w + " "
        else:
            current += w + " "
    if current.strip():
        lines.append(current.strip())
    return lines or [""]


def _box(step: Step) -> str:
    lines = []
    top = "┌" + H_LINE + "┐"
    bottom = "└" + H_LINE + "┘"
    title_line = f"  [{step.name}]"
    lines.append(top)
    lines.append(f"│ {title_line:<{BOX_WIDTH - 2}} │")
    lines.append(f"│{'─' * BOX_WIDTH}│")

    for row in _wrap(step.description):
        lines.append(f"│  {row:<{BOX_WIDTH - 4}}  │")

    lines.append(f"│{'·' * BOX_WIDTH}│")

    lines.append(f"│  {'Çıktılar:':<{BOX_WIDTH - 4}}  │")
    for out in step.outputs:
        for row in _wrap("• " + out):
            lines.append(f"│    {row:<{BOX_WIDTH - 6}}  │")

    if step.depends_on:
        lines.append(f"│{'·' * BOX_WIDTH}│")
        dep_str = "Bağımlı: " + ", ".join(step.depends_on)
        for row in _wrap(dep_str):
            lines.append(f"│  {row:<{BOX_WIDTH - 4}}  │")

    lines.append(bottom)
    return "\n".join(lines)


def render_diagram() -> None:
    header = "=" * (BOX_WIDTH + 2)
    print(header)
    print("  Jarvis-Hermes Araç Zinciri (Tool Chain Flow)")
    print(header)
    print()

    for i, step in enumerate(TOOL_CHAIN):
        print(_box(step))
        if i < len(TOOL_CHAIN) - 1:
            print(CONNECTOR)
            print(ARROW)
            print()

    print()
    print("─" * (BOX_WIDTH + 2))
    print("  Toplam adım:", len(TOOL_CHAIN))
    serials = sum(1 for s in TOOL_CHAIN if s.depends_on)
    print("  Seri (bağımlı) adım:", serials)
    print("  Paralel çalışabilir adım:", len(TOOL_CHAIN) - serials)
    print("─" * (BOX_WIDTH + 2))


if __name__ == "__main__":
    render_diagram()
