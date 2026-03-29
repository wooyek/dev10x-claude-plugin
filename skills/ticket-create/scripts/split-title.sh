#!/usr/bin/env bash
set -euo pipefail

# Split a body file into title and body-only content.
# When --body-file is used without --title, the first line
# of the file is the title, separated from the body by a
# blank line.
#
# Usage: split-title.sh <body-file>
# Output: TITLE=<first line>
#         BODY_FILE=<path to body-only temp file>
#
# The script creates a new temp file for the body-only
# content (via mktmp.sh) and leaves the original file
# untouched.

BODY_FILE="${1:?Usage: split-title.sh <body-file>}"

if [[ ! -f "$BODY_FILE" ]]; then
    echo "Error: File not found: $BODY_FILE" >&2
    exit 1
fi

TITLE=$(head -1 "$BODY_FILE")
if [[ -z "$TITLE" ]]; then
    echo "Error: First line of $BODY_FILE is empty" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BODY_ONLY=$(/tmp/claude/bin/mktmp.sh gh-issue body-only .md)
tail -n +3 "$BODY_FILE" > "$BODY_ONLY"

echo "TITLE=$TITLE"
echo "BODY_FILE=$BODY_ONLY"
