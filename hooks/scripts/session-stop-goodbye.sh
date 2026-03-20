#!/usr/bin/env bash
# Stop hook — goodbye message with community link and resume command.

set -euo pipefail

payload=$(cat)

session_id=$(printf '%s' "$payload" | jq -r '.session_id // empty')

URL="https://www.skool.com/Dev10x-1892"
echo ""
echo "Thank you for using Dev10x. Join the community to get the most out of the plugin:"
printf '\e]8;;%s\e\\%s\e]8;;\e\\\n' "$URL" "$URL"

if [[ -n "$session_id" ]]; then
    echo ""
    echo "Resume this session with:"
    echo "  claude --resume $session_id"
fi
