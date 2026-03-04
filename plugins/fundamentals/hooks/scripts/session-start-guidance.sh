#!/usr/bin/env bash
# SessionStart hook: inject session guidance as additional_context.
# Reads session-guidance.md and outputs it in the hook JSON format
# so Claude receives it as system-level context every session.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUIDANCE_FILE="${SCRIPT_DIR}/session-guidance.md"

if [[ ! -f "$GUIDANCE_FILE" ]]; then
    exit 0
fi

guidance=$(cat "$GUIDANCE_FILE")

escape_for_json() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

escaped=$(escape_for_json "$guidance")

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "${escaped}"
  }
}
EOF
