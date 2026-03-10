#!/bin/bash
# Hook: Validate gh pr create includes the correct --base branch.
#
# Detects the repo's base branch dynamically (develop > development >
# main > master > trunk) and blocks if --base <detected> is missing.
# Pass --force in the gh command to bypass the check intentionally.
#
# Reads tool input from stdin (JSON with tool_input.command field).

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""') || {
    echo "BLOCKED: Hook input parsing failed."
    exit 2
}

# Only check gh pr create commands
if ! echo "$COMMAND" | grep -qP 'gh\s+pr\s+create'; then
    exit 0
fi

# Allow --force to bypass the check
if echo "$COMMAND" | grep -qP '\-\-force'; then
    exit 0
fi

# Detect the repo's base branch
BASE_BRANCH=""
for candidate in develop development main master trunk; do
    if git rev-parse --verify "origin/$candidate" &>/dev/null; then
        BASE_BRANCH="$candidate"
        break
    fi
done

if [ -z "$BASE_BRANCH" ]; then
    echo "BLOCKED: Cannot detect base branch — no develop, main, master, or trunk found on origin."
    echo "Fetch remotes with 'git fetch' and retry."
    exit 2
fi

# Check that --base <detected_branch> is present
if ! echo "$COMMAND" | grep -qP "\-\-base\s+${BASE_BRANCH}"; then
    echo "BLOCKED: gh pr create must include '--base ${BASE_BRANCH}'."
    echo "Add '--base ${BASE_BRANCH}' to the command, or use --force to override."
    exit 2
fi

exit 0
