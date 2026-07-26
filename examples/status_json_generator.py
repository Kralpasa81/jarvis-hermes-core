#!/usr/bin/env python3
"""
Basit bir status JSON üretici örneği.

Tamamen sabit/örnek (synthetic) verilerle bir servis durumu JSON'u üretir --
gerçek bir servis, port veya süreç izlemez; hiçbir dosya, ortam değişkeni
veya ağ kaynağı okumaz.

Usage:
  python3 examples/status_json_generator.py
"""
import json
from datetime import datetime


def generate_status():
    return {
        "service": "jarvis-hermes-core",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "0.0.0-daily",
        "components": {
            "core": {"status": "ok", "uptime": "72h"},
            "scheduler": {"status": "ok", "tasks_pending": 0},
            "examples": {"status": "ok"}
        },
        "checks": [
            {"name": "config_read", "ok": True, "note": "no secrets in repo"},
            {"name": "syntax_check", "ok": True}
        ]
    }


if __name__ == "__main__":
    print(json.dumps(generate_status(), indent=2))
