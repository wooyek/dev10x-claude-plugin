#!/usr/bin/env bash
# Grooming rebase wrapper — uses git-seq-editor.sh as GIT_SEQUENCE_EDITOR.
#
# Usage:
#   GROOM_SEQ_FILE=/tmp/claude/git/rebase-seq.abc123.txt \
#     git-rebase-groom.sh <base-ref>
#
# Before calling: write rebase todo to $GROOM_SEQ_FILE

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEQ_EDITOR="$SCRIPT_DIR/git-seq-editor.sh"

: "${GROOM_SEQ_FILE:?GROOM_SEQ_FILE env var must point to the rebase-seq file}"

if [[ $# -lt 1 ]]; then
    echo "Usage: GROOM_SEQ_FILE=<path> git-rebase-groom.sh <base-ref>" >&2
    exit 1
fi

if [[ ! -f "$GROOM_SEQ_FILE" ]]; then
    echo "ERROR: $GROOM_SEQ_FILE not found." >&2
    echo "Use the Write tool to write the rebase todo to $GROOM_SEQ_FILE first." >&2
    exit 1
fi

if [[ ! -x "$SEQ_EDITOR" ]]; then
    echo "ERROR: $SEQ_EDITOR not found or not executable." >&2
    exit 1
fi

base_ref="$1"
shift

GROOM_SEQ_FILE="$GROOM_SEQ_FILE" \
GIT_SEQUENCE_EDITOR="$SEQ_EDITOR" \
GIT_EDITOR="true" \
    exec git rebase -i "$base_ref" "$@"
