#!/usr/bin/env bash
# Create a unique temp file under /tmp/Dev10x/<namespace>/.
#
# Usage:
#   mktmp.sh <namespace> <prefix> [.ext]
#   mktmp.sh -d <namespace> <prefix>     # create a directory instead
#
# Examples:
#   mktmp.sh git commit-msg .txt         → /tmp/Dev10x/git/commit-msg.XXXXXXXXXXXX.txt
#   mktmp.sh git pr-review .json         → /tmp/Dev10x/git/pr-review.XXXXXXXXXXXX.json
#   mktmp.sh pr-monitor notify .txt      → /tmp/Dev10x/pr-monitor/notify.XXXXXXXXXXXX.txt
#   mktmp.sh skill-audit audit .md       → /tmp/Dev10x/skill-audit/audit.XXXXXXXXXXXX.md
#   mktmp.sh -d git groom               → /tmp/Dev10x/git/groom.XXXXXXXXXXXX/

set -euo pipefail

DIR_MODE=false
if [[ "${1:-}" == "-d" ]]; then
    DIR_MODE=true
    shift
fi

NAMESPACE="${1:?Usage: mktmp.sh [-d] <namespace> <prefix> [.ext]}"
PREFIX="${2:?Usage: mktmp.sh [-d] <namespace> <prefix> [.ext]}"
EXT="${3:-}"

BASEDIR="/tmp/Dev10x/$NAMESPACE"
mkdir -p "$BASEDIR"

TEMPLATE="${PREFIX}.XXXXXXXXXXXX${EXT}"

if $DIR_MODE; then
    mktemp -d --tmpdir="$BASEDIR" "$TEMPLATE"
else
    mktemp --tmpdir="$BASEDIR" "$TEMPLATE"
fi
