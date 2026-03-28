#!/usr/bin/env bash
# SessionStart hook — detect and offer prior session state reload.
# Reads the persisted state file (if any) and plan file (if any)
# and injects them as additionalContext so the agent is aware of
# prior session work and persisted plan state.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

toplevel=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [[ -z "$toplevel" ]]; then
    exit 0
fi

project_hash=$(printf '%s' "$toplevel" | md5sum | cut -d' ' -f1)
state_dir="$HOME/.claude/projects/_session_state"
state_file="$state_dir/${project_hash}.json"
plan_file="$toplevel/.claude/session/plan.yaml"

has_state=false
has_plan=false
[[ -f "$state_file" ]] && has_state=true
[[ -f "$plan_file" ]] && has_plan=true

if [[ "$has_state" == "false" && "$has_plan" == "false" ]]; then
    exit 0
fi

context=""

# --- Session state section ---
if [[ "$has_state" == "true" ]]; then
    timestamp=$(jq -r '.timestamp // empty' < "$state_file")
    if [[ -z "$timestamp" ]]; then
        rm -f "$state_file"
    else
        file_epoch=$(date -d "$timestamp" +%s 2>/dev/null || echo 0)
        now_epoch=$(date +%s)
        age_hours=$(( (now_epoch - file_epoch) / 3600 ))

        if [[ $age_hours -gt 24 ]]; then
            stale_flag=" (STALE — ${age_hours}h old, may be outdated)"
        else
            stale_flag=""
        fi

        branch=$(jq -r '.branch // "unknown"' < "$state_file")
        worktree=$(jq -r '.worktree // ""' < "$state_file")
        session_id=$(jq -r '.session_id // ""' < "$state_file")
        modified=$(jq -r '.modified_files | if length > 0 then map("- " + .) | join("\n") else "none" end' < "$state_file")
        staged=$(jq -r '.staged_files | if length > 0 then map("- " + .) | join("\n") else "none" end' < "$state_file")
        commits=$(jq -r '.recent_commits | if length > 0 then join("\n") else "none" end' < "$state_file")

        context="Prior session state detected${stale_flag}:
- Branch: ${branch}"

        if [[ -n "$worktree" ]]; then
            context+="
- Worktree: ${worktree}"
        fi

        context+="
- Last active: ${timestamp}
- Session ID: ${session_id}

Modified files:
${modified}

Staged files:
${staged}

Recent commits:
${commits}

Resume prior session with: claude --resume ${session_id}"
    fi
fi

# --- Persisted plan section (independent of session state) ---
if [[ "$has_plan" == "true" ]]; then
    plan_json=$("$SCRIPT_DIR/task-plan-sync.py" --json-summary 2>/dev/null || echo "{}")
    plan_status=$(printf '%s' "$plan_json" | jq -r '.plan.status // "unknown"')
    plan_branch=$(printf '%s' "$plan_json" | jq -r '.plan.branch // "unknown"')
    plan_synced=$(printf '%s' "$plan_json" | jq -r '.plan.last_synced // "unknown"')
    task_count=$(printf '%s' "$plan_json" | jq -r '.tasks | length')
    completed_count=$(printf '%s' "$plan_json" | jq -r '[.tasks[] | select(.status == "completed")] | length')
    pending_tasks=$(printf '%s' "$plan_json" | jq -r '
        [.tasks[] | select(.status != "completed" and .status != "deleted")] |
        map("  - [" + .status + "] #" + .id + " " + .subject) |
        join("\n")
    ')

    if [[ -n "$context" ]]; then
        context+="

"
    fi

    context+="Persisted plan detected (${completed_count}/${task_count} tasks completed):
- Plan branch: ${plan_branch}
- Plan status: ${plan_status}
- Last synced: ${plan_synced}"

    if [[ -n "$pending_tasks" && "$pending_tasks" != "null" ]]; then
        context+="
- Remaining tasks:
${pending_tasks}"
    fi

    # Include plan context (work_type, routing table) if available
    work_type=$(printf '%s' "$plan_json" | jq -r '.plan.context.work_type // empty')
    if [[ -n "$work_type" ]]; then
        context+="
- Work type: ${work_type}"
    fi

    tickets=$(printf '%s' "$plan_json" | jq -r '.plan.context.tickets // [] | join(", ")')
    if [[ -n "$tickets" ]]; then
        context+="
- Tickets: ${tickets}"
    fi

    # Include routing table for shipping action guidance
    routing=$(printf '%s' "$plan_json" | jq -r '
        .plan.context.routing_table // {} |
        to_entries |
        if length > 0 then
            map("  " + (.key | tostring) + " → " + (.value | tostring)) | join("\n")
        else empty end
    ')
    if [[ -n "$routing" ]]; then
        context+="
- Skill routing:
${routing}"
    fi

    if [[ "$plan_status" == "completed" ]]; then
        context+="
- All tasks completed. Plan can be archived."
    fi
fi

if [[ -z "$context" ]]; then
    exit 0
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

escaped=$(escape_for_json "$context")

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "${escaped}"
  }
}
EOF

rm -f "$state_file"
