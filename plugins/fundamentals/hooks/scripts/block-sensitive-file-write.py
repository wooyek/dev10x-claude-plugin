#!/usr/bin/env python3
"""PreToolUse hook: block edits to sensitive files (.env, secrets, credentials).

Exit codes: 0=allow, 2=block
"""

from __future__ import annotations

import json
import sys

SENSITIVE_PATTERNS = (".env", "secrets.env", "credentials", ".secret")


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

    fp = data.get("tool_input", {}).get("file_path", "")
    if any(p in fp for p in SENSITIVE_PATTERNS):
        block(f"BLOCKED: Editing sensitive file: {fp}")

    sys.exit(0)


if __name__ == "__main__":
    main()
