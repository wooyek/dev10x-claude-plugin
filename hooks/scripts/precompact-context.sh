#!/usr/bin/env bash
# PreCompact hook — inject structured context summary before compaction.
# Preserves essential conventions, active git state, and working files
# so the agent recovers gracefully after context window compression.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$SCRIPT_DIR/../.."

payload=$(cat) || exit 0

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
toplevel=$(git rev-parse --show-toplevel 2>/dev/null || echo "unknown")
worktree_name=""
if [[ -f "$toplevel/.git" ]]; then
    worktree_name=$(basename "$toplevel")
fi

modified=$(git diff --name-only 2>/dev/null | head -20 || true)
staged=$(git diff --cached --name-only 2>/dev/null | head -20 || true)
untracked=$(git ls-files --others --exclude-standard 2>/dev/null | head -10 || true)

recent_commits=$(git log --oneline -5 2>/dev/null || true)

essentials=""
essentials_file="$PLUGIN_ROOT/.claude/rules/essentials.md"
if [[ -f "$essentials_file" ]]; then
    essentials=$(cat "$essentials_file")
fi

summary="# Post-Compaction Context Recovery

## Git State
- **Branch:** $branch"

if [[ -n "$worktree_name" ]]; then
    summary+="
- **Worktree:** $worktree_name"
fi

summary+="
- **Working directory:** $toplevel"

format_file_list() {
    while IFS= read -r line; do
        [[ -n "$line" ]] && printf -- '- %s\n' "$line"
    done
}

if [[ -n "$modified" ]]; then
    summary+="

### Modified files (unstaged)
$(printf '%s\n' "$modified" | format_file_list)"
fi

if [[ -n "$staged" ]]; then
    summary+="

### Staged files
$(printf '%s\n' "$staged" | format_file_list)"
fi

if [[ -n "$untracked" ]]; then
    summary+="

### Untracked files
$(printf '%s\n' "$untracked" | format_file_list)"
fi

if [[ -n "$recent_commits" ]]; then
    summary+="

### Recent commits
\`\`\`
$recent_commits
\`\`\`"
fi

if [[ -n "$essentials" ]]; then
    summary+="

## Essential Conventions (from essentials.md)
$essentials"
fi

# Inject persisted plan state if available
plan_file="$toplevel/.claude/session/plan.yaml"
if [[ -f "$plan_file" ]]; then
    plan_json=$("$PLUGIN_ROOT/hooks/scripts/task-plan-sync.py" --json-summary 2>/dev/null || echo "{}")
    plan_branch=$(printf '%s' "$plan_json" | jq -r '.plan.branch // "unknown"')
    plan_status=$(printf '%s' "$plan_json" | jq -r '.plan.status // "unknown"')
    work_type=$(printf '%s' "$plan_json" | jq -r '.plan.context.work_type // "unknown"')

    # Rich task summary: include metadata (type, skills) for non-completed tasks
    task_summary=$(printf '%s' "$plan_json" | jq -r '
        .tasks // [] | map(
            if .status == "completed" then
                "- [completed] #" + .id + " " + .subject
            else
                "- [" + .status + "] #" + .id + " " + .subject +
                (if .metadata.type then " (" + .metadata.type + ")" else "" end) +
                (if .metadata.skills then " → " + (.metadata.skills | join(", ")) else "" end)
            end
        ) | join("\n")
    ')

    if [[ -n "$task_summary" ]]; then
        summary+="

## Persisted Plan State
- **Branch:** $plan_branch
- **Plan status:** $plan_status
- **Work type:** $work_type

### Tasks
$task_summary"
    fi

    # Inject routing table from plan context or static fallback
    routing_table=$(printf '%s' "$plan_json" | jq -r '
        .plan.context.routing_table // {} |
        to_entries | map(.key + " → " + .value) | join("\n")
    ')

    if [[ -n "$routing_table" && "$routing_table" != "" ]]; then
        summary+="

### Skill Routing Table (from plan context)
$routing_table"
    else
        # Fallback: inject static routing table
        recovery_file="$PLUGIN_ROOT/references/compaction-recovery.md"
        if [[ -f "$recovery_file" ]]; then
            recovery_content=$(cat "$recovery_file")
            summary+="

$recovery_content"
        fi
    fi

    # Inject gathered context summary if stored
    gathered=$(printf '%s' "$plan_json" | jq -r '.plan.context.gathered_summary // empty')
    if [[ -n "$gathered" ]]; then
        summary+="

### Gathered Context (from Phase 2)
$gathered"
    fi

    summary+="

> Reconstructed from persisted plan file. Use TaskList to verify
> current session state. If tasks are missing, recreate them from
> this list. Use the routing table above for all shipping actions."
fi

escape_for_json() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

escaped=$(escape_for_json "$summary")

printf '{"hookSpecificOutput":{"systemMessage":"%s"}}' "$escaped"
