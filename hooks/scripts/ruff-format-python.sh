#!/usr/bin/env bash
set -euo pipefail

# PostToolUse hook: auto-format Python files with ruff after Edit/Write.
# Reads tool_input JSON from stdin, extracts file_path, runs ruff if .py.

INPUT=$(cat) || exit 0

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty') || exit 0

[[ -z "$FILE_PATH" ]] && exit 0
[[ "$FILE_PATH" != *.py ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0

ruff format "$FILE_PATH" || true
ruff check --fix "$FILE_PATH" || true
