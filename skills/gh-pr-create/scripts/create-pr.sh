#!/usr/bin/env bash
# Create a draft PR with two-pass body generation.
# Usage: create-pr.sh <title> <job_story> <issue_id> [<fixes_url>]
# Outputs the PR number on success.
set -euo pipefail

TITLE="$1"
JOB_STORY="$2"
ISSUE="$3"
FIXES_URL="${4:-}"

FIXES_LINE=""
if [ -n "$FIXES_URL" ]; then
    FIXES_LINE=$(printf '\nFixes %s\n' "$FIXES_URL")
fi

BRANCH_NAME=$(git symbolic-ref --short HEAD)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load checklist template (substitute issue ID placeholder)
CHECKLIST=""
if [ -f .github/checklist.md ]; then
    CHECKLIST=$(sed "s/ISSUE-NO/$ISSUE/" .github/checklist.md)
fi

# Push branch
git push --set-upstream origin "$BRANCH_NAME"

# First pass: create PR with plain commit list + checklist
COMMITS=$(git log origin/develop..HEAD --reverse --format="- %s")
BODY=$(printf '%s\n\n---\n\n%s%s\n\n---\n\n%s' \
    "$JOB_STORY" "$COMMITS" "$FIXES_LINE" "$CHECKLIST")
gh pr create --draft --base develop --title "$TITLE" --body "$BODY"

# Get PR number
PR_NUMBER=$(gh pr view --json number -q .number)

# Second pass: update body with linked commits
LINKED_COMMITS=$("$SCRIPT_DIR/generate-commit-list.sh" "$PR_NUMBER")
FINAL_BODY=$(printf '%s\n\n---\n\n%s%s\n\n---\n\n%s' \
    "$JOB_STORY" "$LINKED_COMMITS" "$FIXES_LINE" "$CHECKLIST")
gh pr edit "$PR_NUMBER" --body "$FINAL_BODY"

echo "$PR_NUMBER"
