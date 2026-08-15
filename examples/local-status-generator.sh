#!/bin/bash
# Local environment status generator
OUTPUT_FILE="local_status_$(date +%Y%m%d%H%M%S).json"

# Collect system info
HOSTNAME=$(hostname)
TIMESTAMP=$(date --iso-8601=seconds)
UPTIME=$(uptime | sed 's/^.*up *//;s/, *[0-9]* user.*//;s/min/minutes/;s/ [0-9:]*//;s/load average: //')
MEMORY=$(free -h | awk '/^Mem:/{print $3 "/" $2 " (" $3/$2*100"% used)"}')

# Generate JSON
cat > "$OUTPUT_FILE" << EOF
{
  "hostname": "$HOSTNAME",
  "timestamp": "$TIMESTAMP", 
  "uptime_summary": "$UPTIME",
  "memory_usage": "$MEMORY",
  "current_user": "$(whoami)",
  "working_directory": "$(pwd)",
  "system_type": "$(uname -s)",
  "architecture": "$(uname -m)" 
}
EOF

echo "Local status saved to: $OUTPUT_FILE"
echo "Content preview:"
cat "$OUTPUT_FILE"