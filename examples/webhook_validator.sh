#!/bin/bash
# Webhook payload validator for Hermes
# Simple script to validate webhook payloads

PAYLOAD=$1

if [ -z "$PAYLOAD" ]; then
    echo "Usage: $0 '{\"key\": \"value\"}'"
    exit 1
fi

# Basic validation checks
if ! echo "$PAYLOAD" | jq empty 2>/dev/null; then
    echo "Invalid JSON payload"
    exit 1
fi

if ! echo "$PAYLOAD" | jq '.event_type' 2>/dev/null | grep -q "\""; then
    echo "Missing event_type field"
    exit 1
fi

if ! echo "$PAYLOAD" | jq '.data' 2>/dev/null | grep -q "\""; then
    echo "Missing data field"
    exit 1
fi

if ! echo "$PAYLOAD" | jq '.signature' 2>/dev/null | grep -q "\""; then
    echo "Missing signature field"
    exit 1
fi

echo "Webhook payload is valid!"
