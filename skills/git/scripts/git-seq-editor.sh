#!/usr/bin/env bash
# GIT_SEQUENCE_EDITOR replacement — reads rebase instructions from
# /tmp/claude/branch-groom/rebase-seq.txt (skill-namespaced data dir).
#
# Usage: GIT_SEQUENCE_EDITOR=~/.claude/skills/git/scripts/git-seq-editor.sh git rebase -i ...
#
# Before running rebase, write the desired todo content to:
#   /tmp/claude/branch-groom/rebase-seq.txt

set -euo pipefail

TODO_FILE="${1:?GIT_SEQUENCE_EDITOR was called without a todo file argument}"
SEQ_SOURCE="/tmp/claude/branch-groom/rebase-seq.txt"

if [[ ! -f "$SEQ_SOURCE" ]]; then
    echo "ERROR: $SEQ_SOURCE not found." >&2
    echo "Write the rebase todo to that file before running git rebase." >&2
    exit 1
fi

cp "$SEQ_SOURCE" "$TODO_FILE"
