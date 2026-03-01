#!/usr/bin/env python3
"""PreToolUse hook: enforce JTBD outcome-focused commit titles.

Intercepts `git commit` commands, extracts the title line, strips
gitmoji + ticket prefix, and blocks if the description starts with
an implementation-focused verb (Add, Update, Remove, etc.).

Skips: fixup!/squash! commits, --amend, merge commits.

Exit codes:
  0 — allow
  2 — block
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_VERB_BASES = [
    "Add",
    "Adjust",
    "Align",
    "Apply",
    "Bump",
    "Change",
    "Clean",
    "Combine",
    "Configure",
    "Consolidate",
    "Delete",
    "Drop",
    "Extend",
    "Extract",
    "Implement",
    "Include",
    "Install",
    "Integrate",
    "Introduce",
    "Merge",
    "Migrate",
    "Modify",
    "Move",
    "Organize",
    "Patch",
    "Pin",
    "Refactor",
    "Register",
    "Remove",
    "Rename",
    "Replace",
    "Revert",
    "Set",
    "Split",
    "Switch",
    "Synchronize",
    "Sync",
    "Update",
    "Wire",
    "Wrap",
]


def _expand_verbs(bases: list[str]) -> list[str]:
    expanded: list[str] = []
    for v in bases:
        expanded.append(v)
        if v.endswith("e"):
            expanded.append(v + "d")
        elif v.endswith("y"):
            expanded.append(v[:-1] + "ied")
        else:
            expanded.append(v + "ed")
        if v.endswith("e"):
            expanded.append(v[:-1] + "ing")
        else:
            expanded.append(v + "ing")
    return expanded


ALL_VERBS = _expand_verbs(_VERB_BASES)

VERB_RE = re.compile(
    r"^(" + "|".join(re.escape(v) for v in ALL_VERBS) + r")\b",
    re.IGNORECASE,
)

TICKET_RE = re.compile(r"^[A-Z]+-\d+\s+")

JTBD_VERBS = (
    "Enable, Allow, Support, Prevent, Ensure, Simplify, Improve, "
    "Optimize, Resolve, Streamline, Protect, Enforce, Automate, "
    "Unblock, Accelerate, Stabilize, Surface, Centralize, "
    "Decouple, Isolate, Harden, Standardize"
)

BLOCK_MSG = (
    "JTBD violation: commit title is implementation-focused.\n"
    "\n"
    "  Title: {title}\n"
    '  Problem: starts with "{verb}" — describes what changed, '
    "not what it enables.\n"
    "\n"
    "Rewrite to describe the user-facing outcome:\n"
    '  Bad:  "Add retry logic to payment service"\n'
    '  Good: "Enable automatic retry on payment failure"\n'
    "\n"
    "Outcome-focused verbs: {jtbd_verbs}\n"
    "\n"
    "Update the commit message in the temp file and retry."
)


def extract_title_from_file(path: str) -> str | None:
    try:
        first_line = Path(path).read_text().splitlines()[0]
        return first_line.strip()
    except (FileNotFoundError, IndexError, OSError):
        return None


def extract_title(command: str) -> str | None:
    match = re.search(r"-F\s+(\S+)", command)
    if match:
        return extract_title_from_file(match.group(1))

    match = re.search(r"""-m\s+(['"])(.*?)\1""", command)
    if match:
        return match.group(2).splitlines()[0].strip()

    match = re.search(r"-m\s+(\S+)", command)
    if match:
        return match.group(1)

    return None


def strip_prefix(title: str) -> str:
    i = 0
    while i < len(title) and not title[i].isascii():
        i += 1
    desc = title[i:].strip()
    desc = TICKET_RE.sub("", desc).strip()
    return desc


def check_jtbd(title: str) -> tuple[bool, str]:
    desc = strip_prefix(title)
    match = VERB_RE.match(desc)
    if match:
        return False, match.group(1)
    return True, ""


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

    if not re.search(r"\bgit\s+commit\b", command):
        sys.exit(0)

    if "--amend" in command or "--fixup" in command:
        sys.exit(0)

    title = extract_title(command)
    if not title:
        sys.exit(0)

    if title.startswith(("fixup!", "squash!", "Merge ")):
        sys.exit(0)

    is_ok, verb = check_jtbd(title)
    if not is_ok:
        block(
            BLOCK_MSG.format(
                title=title,
                verb=verb,
                jtbd_verbs=JTBD_VERBS,
            )
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
