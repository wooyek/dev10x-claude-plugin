#!/usr/bin/env bash
# Stop hook — persist session state for next-session reload.
# Writes branch, modified files, and recent commits to a JSON file
# so the next SessionStart can offer context recovery.

set -euo pipefail

payload=$(cat) || exit 0

session_id=$(printf '%s' "$payload" | jq -r '.session_id // empty')
if [[ -z "$session_id" ]]; then
    exit 0
fi

toplevel=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [[ -z "$toplevel" ]]; then
    exit 0
fi

project_hash=$(printf '%s' "$toplevel" | md5sum | cut -d' ' -f1)
state_dir="$HOME/.claude/projects/_session_state"
mkdir -p "$state_dir"
chmod 700 "$state_dir"
state_file="$state_dir/${project_hash}.json"

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

worktree_name=""
if [[ -f "$toplevel/.git" ]]; then
    worktree_name=$(basename "$toplevel")
fi

modified_json=$(git diff --name-only 2>/dev/null | head -20 | jq -R -s 'split("\n") | map(select(. != ""))') || modified_json="[]"
staged_json=$(git diff --cached --name-only 2>/dev/null | head -20 | jq -R -s 'split("\n") | map(select(. != ""))') || staged_json="[]"
recent_commits_json=$(git log --oneline -5 2>/dev/null | jq -R -s 'split("\n") | map(select(. != ""))') || recent_commits_json="[]"

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

has_plan="false"
if [[ -f "$toplevel/.claude/session/plan.yaml" ]]; then
    has_plan="true"
fi

jq -n \
    --arg session_id "$session_id" \
    --arg branch "$branch" \
    --arg worktree "$worktree_name" \
    --arg toplevel "$toplevel" \
    --arg timestamp "$timestamp" \
    --argjson modified "$modified_json" \
    --argjson staged "$staged_json" \
    --argjson recent_commits "$recent_commits_json" \
    --argjson has_plan "$has_plan" \
    '{
        session_id: $session_id,
        branch: $branch,
        worktree: $worktree,
        working_directory: $toplevel,
        timestamp: $timestamp,
        modified_files: $modified,
        staged_files: $staged,
        recent_commits: $recent_commits,
        has_plan: $has_plan
    }' > "$state_file"
