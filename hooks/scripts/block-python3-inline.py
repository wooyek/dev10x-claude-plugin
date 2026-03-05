#!/usr/bin/env python3
"""PreToolUse hook: block python3 inline scripts and untrusted script paths.

Blocks:
  1. python3 -c "..."  — inline code (always)
  2. python3 /abs/path where path is not in the approved whitelist

Allowed python3 invocations:
  - python3 -m <module>         module invocations (json.tool, pytest, etc.)
  - python3 ~/.claude/tools/**  trusted tool scripts
  - python3 ~/.claude/skills/** trusted skill scripts
  - python3 ~/.claude/hooks/**  trusted hook scripts
  - python3 <relative-path>     project-local scripts (manage.py, etc.)

Instructs to use Write + uv run --script pattern instead.

Exit codes: 0=allow, 2=block
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys

APPROVED_ABS_PREFIXES = (
    os.path.expanduser("~/.claude/tools/"),
    os.path.expanduser("~/.claude/skills/"),
    os.path.expanduser("~/.claude/hooks/"),
)

BLOCK_MSG = """\
\U0001f6ab  python3 inline/untrusted script blocked.

Use the Write tool to create a self-contained uv script instead:

  Step 1 — Write the script to /tmp/claude/<name>.py via the Write tool:

    #!/usr/bin/env -S uv run --script
    # /// script
    # requires-python = ">=3.11"
    # dependencies = []  # add packages here if needed, e.g. ["requests"]
    # ///

    # your code here

  Step 2 — Run it:

    uv run --script /tmp/claude/<name>.py

Benefits:
  - Reproducible: deps declared inline (PEP 723), no pip install needed
  - Auditable: Write tool diffs show exactly what runs
  - Permitted: uv run:* is pre-approved; /tmp/claude/ is writable

If the script needs no third-party deps, the # /// block can be omitted.
"""

ENV_VAR_RE = re.compile(r"^[A-Z_][A-Z0-9_]*=\S*$")


def strip_env_prefix(parts: list[str]) -> list[str]:
    i = 0
    while i < len(parts) and ENV_VAR_RE.match(parts[i]):
        i += 1
    return parts[i:]


def is_approved(path: str) -> bool:
    expanded = os.path.expanduser(path)
    return any(
        expanded.startswith(p) or path.startswith(p) for p in APPROVED_ABS_PREFIXES
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

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")

    if "python3" not in command:
        sys.exit(0)

    first_cmd = command.split("|")[0].strip()

    try:
        parts = shlex.split(first_cmd)
    except ValueError:
        sys.exit(0)

    parts = strip_env_prefix(parts)

    if not parts or parts[0] != "python3":
        sys.exit(0)

    argv = parts[1:]

    if "-m" in argv:
        sys.exit(0)

    if any(a == "-c" or a.startswith("-c") for a in argv):
        block(BLOCK_MSG)

    script = next(
        (a for a in argv if not a.startswith("-")),
        None,
    )

    if script is None or not os.path.isabs(os.path.expanduser(script)):
        sys.exit(0)

    if is_approved(script):
        sys.exit(0)

    block(BLOCK_MSG)


if __name__ == "__main__":
    main()
