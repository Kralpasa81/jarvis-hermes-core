#!/bin/bash
# HTML entity encoder
# Simple script to encode special characters to HTML entities

TEXT=$1

if [ -z "$TEXT" ]; then
    echo "Usage: $0 'Text to encode'"
    exit 1
fi

echo "$TEXT" | sed 's/&/\&amp;/g; s/<//\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g; s/'"'"'/\&#39;/g'
