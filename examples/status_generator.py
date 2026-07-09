#!/usr/bin/env python3
"""
Simple status JSON generator for jarvis-hermes-core examples.
No network, no keys, harmless.
"""
import json
import platform
from datetime import datetime
status = {
    "project": "jarvis-hermes-core",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "os": platform.system(),
    "python": platform.python_version(),
    "note": "Harmless local status generator. No secrets."
}
print(json.dumps(status, indent=2))
