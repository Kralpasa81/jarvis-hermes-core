#!/usr/bin/env python3
"""
event_log_formatter.py
======================
Jarvis/Hermes örnek aracı: Yapılandırılmış event verilerini
insanın okuyabileceği metin formatına dönüştürür.

Kullanım:
    python3 event_log_formatter.py

Gereksinim: Sadece Python standart kütüphane. Token/API key yok.
"""

import json
from datetime import datetime, timezone


# Örnek event verisi (gerçek bir sistemde JSON dosyasından veya queue'dan gelir)
SAMPLE_EVENTS = [
    {
        "timestamp": "2026-07-10T08:00:01Z",
        "level": "INFO",
        "source": "jarvis.core.boot",
        "message": "Jarvis core başlatıldı.",
        "metadata": {"version": "0.3.1", "mode": "offline"},
    },
    {
        "timestamp": "2026-07-10T08:00:03Z",
        "level": "INFO",
        "source": "jarvis.module.loader",
        "message": "Modül yükleme tamamlandı.",
        "metadata": {"modules_loaded": 4, "modules_skipped": 1},
    },
    {
        "timestamp": "2026-07-10T08:00:05Z",
        "level": "WARN",
        "source": "jarvis.config.validator",
        "message": "Opsiyonel 'telemetry.endpoint' alanı tanımlanmamış; varsayılan kullanılıyor.",
        "metadata": {"field": "telemetry.endpoint", "fallback": "disabled"},
    },
    {
        "timestamp": "2026-07-10T08:00:07Z",
        "level": "INFO",
        "source": "jarvis.hermes.bridge",
        "message": "Hermes köprüsü hazır, bağlantı bekleniyor.",
        "metadata": {"protocol": "local-ipc", "timeout_sec": 30},
    },
    {
        "timestamp": "2026-07-10T08:00:12Z",
        "level": "ERROR",
        "source": "jarvis.plugin.external",
        "message": "Harici eklenti yüklenemedi; atlanıyor.",
        "metadata": {"plugin": "mock-ext-plugin", "reason": "manifest eksik"},
    },
    {
        "timestamp": "2026-07-10T08:00:15Z",
        "level": "INFO",
        "source": "jarvis.core.ready",
        "message": "Sistem hazır. Komut bekleniyor.",
        "metadata": {"uptime_ms": 14000},
    },
]

# Seviyelere göre görsel etiketler
LEVEL_LABELS = {
    "INFO":  "[INFO ] ",
    "WARN":  "[WARN ] ",
    "ERROR": "[ERROR] ",
    "DEBUG": "[DEBUG] ",
}

# Seviyelere göre sıralama önceliği (düşük = önce)
LEVEL_ORDER = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3}


def parse_timestamp(ts_str: str) -> datetime:
    """ISO 8601 UTC timestamp'i datetime nesnesine dönüştürür."""
    return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))


def format_event(event: dict) -> str:
    """Tek bir event'i okunabilir metin satırına dönüştürür."""
    ts = parse_timestamp(event["timestamp"])
    local_ts = ts.strftime("%Y-%m-%d %H:%M:%S UTC")
    label = LEVEL_LABELS.get(event["level"], f"[{event['level']}] ")
    source = event.get("source", "unknown")
    message = event.get("message", "")
    return f"{local_ts}  {label}  {source:<35}  {message}"


def format_metadata(metadata: dict, indent: int = 4) -> str:
    """Metadata sözlüğünü girintili JSON olarak döndürür."""
    if not metadata:
        return ""
    pad = " " * indent
    lines = json.dumps(metadata, ensure_ascii=False, indent=2).splitlines()
    return "\n".join(pad + line for line in lines)


def count_by_level(events: list) -> dict:
    """Her seviyedeki event sayısını döndürür."""
    counts = {}
    for e in events:
        lvl = e.get("level", "UNKNOWN")
        counts[lvl] = counts.get(lvl, 0) + 1
    return counts


def filter_by_level(events: list, min_level: str = "INFO") -> list:
    """Belirtilen minimum seviye ve üzerindeki event'leri filtreler."""
    min_order = LEVEL_ORDER.get(min_level, 0)
    return [e for e in events if LEVEL_ORDER.get(e.get("level", ""), 0) >= min_order]


def print_report(events: list, show_metadata: bool = True) -> None:
    """Event listesini biçimlendirilmiş rapor olarak yazdırır."""
    print("=" * 80)
    print("  JARVIS / HERMES  —  Event Log Raporu")
    print(f"  Oluşturulma: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 80)
    print()

    if not events:
        print("  (Gösterilecek event yok.)")
        print()
        return

    for event in events:
        print(format_event(event))
        if show_metadata and event.get("metadata"):
            print(format_metadata(event["metadata"]))
        print()

    counts = count_by_level(events)
    print("-" * 80)
    print("  Özet:")
    for lvl in ["INFO", "WARN", "ERROR", "DEBUG"]:
        if lvl in counts:
            print(f"    {LEVEL_LABELS[lvl].strip():<8}  {counts[lvl]} adet")
    print(f"    Toplam    :  {len(events)} event")
    print("=" * 80)


def main() -> None:
    print("\n--- Tüm event'ler (INFO ve üzeri) ---\n")
    filtered = filter_by_level(SAMPLE_EVENTS, min_level="INFO")
    print_report(filtered, show_metadata=True)

    print("\n--- Sadece WARN ve ERROR seviyeleri ---\n")
    critical = filter_by_level(SAMPLE_EVENTS, min_level="WARN")
    print_report(critical, show_metadata=False)


if __name__ == "__main__":
    main()
