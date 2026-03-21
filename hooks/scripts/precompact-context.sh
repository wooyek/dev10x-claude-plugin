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
