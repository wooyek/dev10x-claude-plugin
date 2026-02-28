#!/usr/bin/env bash
# Wrapper for extract-session.py — creates output dir and runs extraction.
# Usage: extract-session.sh <jsonl-path> [output.md]
#   If output.md is omitted, writes to stdout.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="/tmp/claude/skill-audit"

mkdir -p "$OUTPUT_DIR"

exec python3 "$SCRIPT_DIR/extract-session.py" "$@"
