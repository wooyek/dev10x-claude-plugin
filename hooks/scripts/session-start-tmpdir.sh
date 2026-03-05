#!/usr/bin/env bash
# SessionStart hook
# Creates /tmp/claude/<session_id>/ scratch directory for the session
# and installs bin/mktmp.sh to /tmp/claude/bin/ for stable path access.

set -euo pipefail

session_id=$(jq -r '.session_id // empty')

if [[ -z "$session_id" ]]; then
    exit 0
fi

mkdir -p "/tmp/claude/$session_id"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_BIN="$SCRIPT_DIR/../../bin"
DEST_BIN="/tmp/claude/bin"

mkdir -p "$DEST_BIN"
cp "$PLUGIN_BIN/mktmp.sh" "$DEST_BIN/mktmp.sh"
chmod +x "$DEST_BIN/mktmp.sh"
