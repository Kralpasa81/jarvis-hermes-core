"""
capability_matrix_builder.py
────────────────────────────
Jarvis Hermes Core — Examples
Date: 2026-07-11

Verilen bir modül listesini (Python dict olarak tanımlı) alır;
her modülü önceden tanımlı yetenek kategorilerine göre değerlendirir
ve bir Capability Matrix raporu üretir.

Hiçbir harici bağımlılık, API anahtarı veya ağ bağlantısı gerektirmez.
Çalıştırmak için: python3 capability_matrix_builder.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List

# ─── Yetenek Kategorileri ───────────────────────────────────────────────────
CATEGORIES = ["INPUT", "PROCESSING", "OUTPUT", "SECURITY", "INTEGRATION"]

# ─── Örnek Modül Tanımları ──────────────────────────────────────────────────
# Gerçek bir sistemde bu bilgiler YAML/JSON dosyasından okunur.
# Burada tamamen kurgusal, güvenli örnek verilerle çalışıyoruz.
SAMPLE_MODULES: List[Dict] = [
    {
        "name": "voice_listener",
        "description": "Mikrofon girdisini alıp metin segmentlerine dönüştürür.",
        "capabilities": ["INPUT"],
        "status": "planned",
        "notes": "Gerçek implementasyon yerel STT modeli kullanacak.",
    },
    {
        "name": "intent_classifier",
        "description": "Ham metni alıp niyet sınıfına eşler.",
        "capabilities": ["PROCESSING"],
        "status": "in_progress",
        "notes": "Kural tabanlı ilk versiyon; ML versiyonu roadmap'te.",
    },
    {
        "name": "task_dispatcher",
        "description": "Niyet sınıfına göre ilgili modülü tetikler.",
        "capabilities": ["PROCESSING", "INTEGRATION"],
        "status": "in_progress",
        "notes": "Öncelik sırası ve zaman aşımı yönetimi henüz yok.",
    },
    {
        "name": "response_renderer",
        "description": "Üretilen yanıtı sesli veya metin olarak kullanıcıya sunar.",
        "capabilities": ["OUTPUT"],
        "status": "planned",
        "notes": "TTS entegrasyonu gerekiyor.",
    },
    {
        "name": "secret_vault_proxy",
        "description": "Modüller arası credential akışını izole eder; sır sızdırmaz.",
        "capabilities": ["SECURITY", "INTEGRATION"],
        "status": "planned",
        "notes": "Çevre değişkenlerinden değil, şifrelenmiş yerelden okur.",
    },
    {
        "name": "log_aggregator",
        "description": "Tüm modüllerden gelen log satırlarını toplar ve filtreler.",
        "capabilities": ["OUTPUT", "SECURITY"],
        "status": "complete",
        "notes": "PII maskeleme aktif; raw loglar dışarı çıkmaz.",
    },
    {
        "name": "config_loader",
        "description": "Uygulama yapılandırmasını okur ve schema'ya göre doğrular.",
        "capabilities": ["INPUT", "PROCESSING"],
        "status": "complete",
        "notes": "JSON Schema tabanlı doğrulama mevcut.",
    },
]

STATUS_SYMBOL = {
    "complete": "✅",
    "in_progress": "🔄",
    "planned": "⬜",
    "deprecated": "❌",
}


@dataclass
class MatrixRow:
    name: str
    description: str
    capabilities: List[str]
    status: str
    notes: str
    flags: Dict[str, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.flags = {cat: (cat in self.capabilities) for cat in CATEGORIES}


def build_matrix(modules: List[Dict]) -> List[MatrixRow]:
    return [MatrixRow(**m) for m in modules]


def render_text_table(rows: List[MatrixRow]) -> str:
    col_w = 22
    cat_w = 5
    header_parts = [f"{'Module':<{col_w}}"] + [f"{c:<{cat_w}}" for c in CATEGORIES] + ["Status   ", "Notes"]
    header = "  ".join(header_parts)
    separator = "─" * len(header)

    lines = [separator, header, separator]
    for row in rows:
        flag_cells = ["  ✓  " if row.flags[c] else "  ·  " for c in CATEGORIES]
        status_cell = f"{STATUS_SYMBOL.get(row.status, '?')} {row.status:<10}"
        line = f"  ".join(
            [f"{row.name:<{col_w}}"]
            + flag_cells
            + [status_cell, row.notes[:40]]
        )
        lines.append(line)
    lines.append(separator)
    return "\n".join(lines)


def category_coverage_report(rows: List[MatrixRow]) -> Dict[str, int]:
    return {cat: sum(1 for r in rows if r.flags[cat]) for cat in CATEGORIES}


def gap_analysis(rows: List[MatrixRow]) -> List[str]:
    """Hiçbir tamamlanmış modülün karşılamadığı kategorileri döndürür."""
    complete_rows = [r for r in rows if r.status == "complete"]
    covered = {cat for r in complete_rows for cat, has in r.flags.items() if has}
    return [cat for cat in CATEGORIES if cat not in covered]


def to_json_summary(rows: List[MatrixRow]) -> str:
    summary = [
        {
            "module": r.name,
            "status": r.status,
            "capabilities": r.capabilities,
        }
        for r in rows
    ]
    return json.dumps(summary, ensure_ascii=False, indent=2)


def main() -> None:
    print("=" * 70)
    print("  Jarvis Hermes Core — Capability Matrix Builder")
    print("  Date: 2026-07-11")
    print("=" * 70)

    rows = build_matrix(SAMPLE_MODULES)

    print("\n📊 Capability Matrix:\n")
    print(render_text_table(rows))

    coverage = category_coverage_report(rows)
    print("\n📈 Kategori Kapsama (toplam modül sayısına göre):")
    for cat, count in coverage.items():
        bar = "█" * count + "░" * (len(rows) - count)
        print(f"  {cat:<12} {bar}  ({count}/{len(rows)})")

    gaps = gap_analysis(rows)
    if gaps:
        print(f"\n⚠️  Tamamlanmış modülsüz kategoriler: {', '.join(gaps)}")
        print("   → Bu kategoriler için en az bir 'complete' modül hedeflenmeli.")
    else:
        print("\n✅ Tüm kategoriler en az bir tamamlanmış modül tarafından karşılanıyor.")

    print("\n📋 JSON Özeti (pipeline entegrasyonu için):")
    print(to_json_summary(rows))

    print("\n" + "=" * 70)
    print("  Not: Bu çıktı gerçek credential veya kişisel veri içermez.")
    print("  Tüm veriler kurgusal örnek amaçlıdır.")
    print("=" * 70)


if __name__ == "__main__":
    main()
