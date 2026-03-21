#!/usr/bin/env bash
# PostToolUse hook (Skill matcher) — track skill invocation metrics.
# Appends skill name and timestamp to a per-session JSON-lines file.
# Minimal latency impact: single jq parse + file append.

set -euo pipefail

payload=$(cat) || exit 0

skill_name=$(printf '%s' "$payload" | jq -r '.tool_input.skill // empty')
if [[ -z "$skill_name" ]]; then
    exit 0
fi

session_id=$(printf '%s' "$payload" | jq -r '.session_id // empty')
if [[ -z "$session_id" ]]; then
    exit 0
fi

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
date_tag=$(date -u +"%Y-%m-%d")

toplevel=$(git rev-parse --show-toplevel 2>/dev/null || echo "unknown")
project_hash=$(printf '%s' "$toplevel" | md5sum | cut -d' ' -f1)

metrics_dir="$HOME/.claude/projects/_metrics"
mkdir -p "$metrics_dir"

metrics_file="$metrics_dir/${project_hash}_${date_tag}.jsonl"

jq -n -c \
    --arg skill "$skill_name" \
    --arg session "$session_id" \
    --arg ts "$timestamp" \
    '{skill: $skill, session: $session, timestamp: $ts}' >> "$metrics_file"

find "$metrics_dir" -name "*.jsonl" -mtime +30 -delete 2>/dev/null
