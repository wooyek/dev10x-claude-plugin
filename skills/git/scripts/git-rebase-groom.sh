#!/usr/bin/env bash
# Grooming rebase wrapper — uses git-seq-editor.sh as GIT_SEQUENCE_EDITOR,
# reading the sequence from /tmp/claude/branch-groom/rebase-seq.txt.
#
# Usage:
#   git-rebase-groom.sh <base-ref>
#   git-rebase-groom.sh $(git merge-base <base-branch> HEAD)
#
# Before calling: write rebase todo to /tmp/claude/branch-groom/rebase-seq.txt

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEQ_EDITOR="$SCRIPT_DIR/git-seq-editor.sh"
SEQ_SOURCE="/tmp/claude/branch-groom/rebase-seq.txt"

mkdir -p /tmp/claude/branch-groom

if [[ $# -lt 1 ]]; then
    echo "Usage: git-rebase-groom.sh <base-ref>" >&2
    exit 1
fi

if [[ ! -f "$SEQ_SOURCE" ]]; then
    echo "ERROR: $SEQ_SOURCE not found." >&2
    echo "Use the Write tool to write the rebase todo to $SEQ_SOURCE first." >&2
    exit 1
fi

if [[ ! -x "$SEQ_EDITOR" ]]; then
    echo "ERROR: $SEQ_EDITOR not found or not executable." >&2
    exit 1
fi

base_ref="$1"
shift

GIT_SEQUENCE_EDITOR="$SEQ_EDITOR" \
GIT_EDITOR="true" \
    exec git rebase -i "$base_ref" "$@"
