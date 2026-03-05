#!/usr/bin/env python3
"""PreToolUse hook: detect && chaining that causes permission friction.

When a setup command (mkdir, cd, export, etc.) is prepended via &&
to a path-based command that has its own allow rule, the combined
command's prefix no longer matches that allow rule — causing a
permission prompt for an otherwise-approved operation.

On detection, blocks and instructs the agent to find or create a
wrapper (fish function, git alias, or ~/.claude/tools/ script) so
the setup is encapsulated and the combined call has a stable prefix.

Exit codes: 0=allow, 2=block
"""

from __future__ import annotations

import json
import os
import re
import sys

SETTINGS_FILES = [
    os.path.expanduser("~/.claude/settings.local.json"),
    os.path.expanduser("~/.claude/settings.json"),
]

SETUP_TOKENS = frozenset(
    ["mkdir", "cd", "export", "source", ".", "pushd", "popd", "touch", "unset"]
)

PATH_PREFIXES = (
    os.path.expanduser("~/.claude/skills/"),
    os.path.expanduser("~/.claude/tools/"),
    os.path.expanduser("~/.claude/hooks/"),
    "~/.claude/skills/",
    "~/.claude/tools/",
    "~/.claude/hooks/",
)

ADVICE = """\
\u26a0\ufe0f  && chaining detected \u2014 permission friction risk.

The setup command before && shifts the effective command prefix away from
the path-based command that has its own allow rule. The allow rule for the
path-based command won't fire.

Fix this by finding or creating a wrapper:

  1. Existing fish functions:
       ls ~/.config/fish/functions/

  2. Existing git aliases:
       git config --list | grep alias\\.

  3. Existing Claude tools / skill scripts:
       ls ~/.claude/tools/
       find ~/.claude/skills -name '*.sh' | head -20

  4. If no wrapper exists, create ~/.claude/tools/<name>.sh that
     handles both the setup and the command internally, then add:
       Bash(~/.claude/tools/<name>:*)   to settings.local.json allow rules

  5. For independent steps, use separate Bash tool calls instead of &&.

Rewrite the command and resubmit.
"""


def load_all_allow_patterns() -> list[str]:
    patterns: list[str] = []
    for path in SETTINGS_FILES:
        try:
            with open(path) as f:
                data = json.load(f)
            for rule in data.get("permissions", {}).get("allow", []):
                m = re.match(r"^Bash\((.+?)(?::\*)?\)$", rule)
                if m:
                    patterns.append(m.group(1))
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    return patterns


def split_on_and(command: str) -> list[str]:
    return [s.strip() for s in re.split(r"\s*&&\s*", command) if s.strip()]


def first_token(segment: str) -> str:
    tokens = segment.split()
    return tokens[0] if tokens else ""


def is_path_based(segment: str) -> bool:
    expanded = os.path.expanduser(segment)
    return any(expanded.startswith(p) or segment.startswith(p) for p in PATH_PREFIXES)


def matches_allow_rule(segment: str, patterns: list[str]) -> str | None:
    expanded_seg = os.path.expanduser(segment)
    for pattern in patterns:
        expanded_pat = os.path.expanduser(pattern)
        if expanded_seg.startswith(expanded_pat) or segment.startswith(pattern):
            return pattern
    return None


def block(detail: str) -> None:
    result = {
        "hookSpecificOutput": {"permissionDecision": "deny"},
        "systemMessage": ADVICE + "\nDetected: " + detail,
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

    if "&&" not in command:
        sys.exit(0)

    segments = split_on_and(command)
    if len(segments) < 2:
        sys.exit(0)

    setup_token = first_token(segments[0])
    if setup_token not in SETUP_TOKENS:
        sys.exit(0)

    allow_patterns = load_all_allow_patterns()

    for i, seg in enumerate(segments[1:], start=2):
        if is_path_based(seg):
            matched = matches_allow_rule(seg, allow_patterns)
            rule_hint = f"Bash({matched}:*)" if matched else "a path-based allow rule"
            block(
                f"segment {i} '{seg[:70]}' would be approved by {rule_hint} "
                f"but the command starts with '{setup_token}'"
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
