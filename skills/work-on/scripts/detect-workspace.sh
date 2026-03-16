#!/usr/bin/env bash
# detect-workspace.sh — Detect current workspace state for work-on skill.
#
# Usage:
#   detect-workspace.sh
#
# Output: KEY=VALUE lines:
#   WORKSPACE=worktree|main-repo
#   BRANCH=feature/my-branch

set -euo pipefail

if [ -f .git ]; then
    WORKSPACE="worktree"
else
    WORKSPACE="main-repo"
fi

BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")

echo "WORKSPACE=$WORKSPACE"
echo "BRANCH=$BRANCH"
