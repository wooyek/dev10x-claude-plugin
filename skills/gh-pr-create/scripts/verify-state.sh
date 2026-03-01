#!/usr/bin/env bash
# Verify branch state before creating a PR.
# Exits with code 1 on validation failure, printing the error message.
# On success, prints: BRANCH_NAME=<name> ISSUE=<ticket-id>
set -euo pipefail

BRANCH_NAME=$(git symbolic-ref --short HEAD)

# Cannot create PR from protected branches
if [[ "$BRANCH_NAME" =~ ^(develop|main|master)$ ]]; then
    echo "❌ Cannot create PR from $BRANCH_NAME. Checkout a feature branch first." >&2
    exit 1
fi

# Check for uncommitted changes (ignore untracked files — they don't affect the PR)
if [ -n "$(git status --porcelain | grep -v '^??')" ]; then
    echo "⚠️  You have uncommitted changes. Commit them first before creating a PR." >&2
    exit 1
fi

# Check if branch has commits ahead of develop
COMMITS_AHEAD=$(git log origin/develop..HEAD --oneline)
if [ -z "$COMMITS_AHEAD" ]; then
    echo "⚠️  No commits to create PR from. Make some changes first." >&2
    exit 1
fi

# Check if branch contains master/main-only commits (not on develop).
# Skip this check if neither origin/master nor origin/main exists
# (develop-only repos would crash with "ambiguous argument 'origin/master'").
MASTER_REF=""
if git rev-parse --verify origin/master &>/dev/null; then
    MASTER_REF="origin/master"
elif git rev-parse --verify origin/main &>/dev/null; then
    MASTER_REF="origin/main"
fi

if [ -n "$MASTER_REF" ]; then
    TOTAL_AHEAD=$(git log origin/develop..HEAD --oneline | wc -l)
    WITHOUT_MASTER=$(git log origin/develop..HEAD --oneline --not "$MASTER_REF" | wc -l)
    if [ "$WITHOUT_MASTER" -lt "$TOTAL_AHEAD" ]; then
        echo "⚠️  This branch includes commits from $MASTER_REF not on develop." >&2
        echo "The PR would target $MASTER_REF instead of develop." >&2
        echo "Rebase first: git rebase --onto origin/develop $MASTER_REF" >&2
        exit 1
    fi
fi

# Extract ticket ID from branch name (username/TICKET-ID/description)
ISSUE=$(echo "$BRANCH_NAME" | cut -d'/' -f2)

echo "BRANCH_NAME=$BRANCH_NAME"
echo "ISSUE=$ISSUE"
