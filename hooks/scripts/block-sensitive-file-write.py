#!/usr/bin/env python3
"""PreToolUse hook: block edits to sensitive files (.env, secrets, credentials).

Exit codes: 0=allow, 2=block
"""

from __future__ import annotations

import json
import sys

SENSITIVE_NAMES = {".env", "secrets.env", ".secret"}
SENSITIVE_SUBSTRINGS = ("credentials",)


def block(message: str) -> None:
    result = {
        "hookSpecificOutput": {"permissionDecision": "deny"},
        "systemMessage": message,
    }
    print(json.dumps(result), file=sys.stderr)
    sys.exit(2)


def _basename(path: str) -> str:
    return path.rsplit("/", 1)[-1] if "/" in path else path


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    fp = data.get("tool_input", {}).get("file_path", "")
    name = _basename(fp)
    if name in SENSITIVE_NAMES or name.startswith((".env.", "secrets.env.")):
        block(f"BLOCKED: Editing sensitive file: {fp}")
    if any(p in fp for p in SENSITIVE_SUBSTRINGS):
        block(f"BLOCKED: Editing sensitive file: {fp}")

    sys.exit(0)


if __name__ == "__main__":
    main()
