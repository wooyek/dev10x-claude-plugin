#!/usr/bin/env python3
"""PreToolUse hook: block eval patterns in skill file edits.

Extracted from validate-bash-security.py (Edit|Write branch only).
The Bash validation branch moved to bash_validators/execution_safety.py.

Exit codes:
  0 — allow
  2 — block
"""

from __future__ import annotations

import json
import re
import sys

EVAL_IN_SKILLS_RE = re.compile(r"\beval\s+[\"$]")
SKILL_PATH_RE = re.compile(r"/\.claude/skills/.*\.(md|sh)$")

EVAL_MSG = (
    "eval is not allowed in skill files — it executes arbitrary code"
    " via double expansion.\n"
    'Use source <(script.sh) instead of eval "$(script.sh)"'
)


def block(message: str) -> None:
    result = {
        "hookSpecificOutput": {"permissionDecision": "deny"},
        "systemMessage": message,
    }
    print(json.dumps(result), file=sys.stderr)
    sys.exit(2)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool = data.get("tool_name", "")
    if tool not in ("Edit", "Write"):
        sys.exit(0)

    inp = data.get("tool_input", {})
    path = inp.get("file_path", "")
    text = inp.get("new_string") or inp.get("content", "")

    if SKILL_PATH_RE.search(path) and EVAL_IN_SKILLS_RE.search(text):
        block(EVAL_MSG)

    sys.exit(0)


if __name__ == "__main__":
    main()
