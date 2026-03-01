#!/usr/bin/env bash
# PreToolUse hook (matcher: Skill)
# Creates /tmp/claude/<skill-name>/ scratch directory before skill runs.
# Reads tool_input.skill from stdin JSON, sanitizes it for path safety.

set -euo pipefail

INPUT=$(cat)
SKILL_NAME=$(echo "$INPUT" | jq -r '.tool_input.skill // empty')

if [[ -z "$SKILL_NAME" ]]; then
  exit 0
fi

# Sanitize: replace colons with dashes, strip anything not alnum/dash/underscore/dot
SAFE_NAME=$(echo "$SKILL_NAME" | tr ':' '-' | sed 's/[^a-zA-Z0-9._-]//g')

if [[ -n "$SAFE_NAME" ]]; then
  mkdir -p "/tmp/claude/${SAFE_NAME}"
fi
