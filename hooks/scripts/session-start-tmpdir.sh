#!/usr/bin/env bash
# SessionStart hook
# Creates /tmp/claude/<session_id>/ scratch directory for the session.

set -euo pipefail

session_id=$(jq -r '.session_id // empty')

if [[ -z "$session_id" ]]; then
    exit 0
fi

mkdir -p "/tmp/claude/$session_id"
