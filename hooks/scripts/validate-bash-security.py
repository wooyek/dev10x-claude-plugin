#!/usr/bin/env python3
"""PreToolUse hook: block shell-based file writes, eval, and env-prefix patterns.

Blocks:
  1. cat >, cat <<, echo >, printf > — use Write/Edit tools instead
  2. eval "$(...)" in skill files — use source <(script.sh) instead
  3. GIT_SEQUENCE_EDITOR=... git — use git develop-rebase alias instead

Exit codes:
  0 — allow
  2 — block
"""

from __future__ import annotations

import json
import re
import sys

SHELL_WRITE_RE = re.compile(
    r"\bcat\b\s*(>|<<|>\s*\S)"
    r"|\becho\b\s+.*\s*(>|>>)\s*\S"
    r"|\bprintf\b.*\s*(>|>>)\s*\S"
    r"|\$\(printf\b"
)

GIT_SEQ_EDITOR_RE = re.compile(r"^GIT_SEQUENCE_EDITOR\s*=")

EVAL_IN_SKILLS_RE = re.compile(r"\beval\s+[\"$]")
SKILL_PATH_RE = re.compile(r"/\.claude/skills/.*\.(md|sh)$")

SHELL_WRITE_MSG = (
    "Use the Write/Edit tool instead of cat/echo/printf redirects.\n"
    "For multi-line commit messages: create a unique file with"
    " /tmp/claude/bin/mktmp.sh git commit-msg .txt,"
    " Write content to the returned path, then git commit -F <path>"
)

EVAL_MSG = (
    "eval is not allowed in skill files — it executes arbitrary code"
    " via double expansion.\n"
    'Use source <(script.sh) instead of eval "$(script.sh)"'
)

GIT_SEQ_EDITOR_MSG = (
    "⚠️  GIT_SEQUENCE_EDITOR=... prefix blocked — permission friction risk.\n\n"
    "The env-var prefix shifts the effective command prefix, breaking allow-rule\n"
    "matching for `git rebase`.\n\n"
    "Use the git aliases instead:\n"
    "  git develop-rebase    — interactive rebase onto develop\n"
    "  git develop-log       — log since diverging from develop\n"
    "  git develop-diff      — diff since diverging from develop\n\n"
    "If aliases are missing, run: /dev10x:git-alias-setup"
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
    inp = data.get("tool_input", {})

    if tool == "Bash":
        command = inp.get("command", "")
        if SHELL_WRITE_RE.search(command):
            block(SHELL_WRITE_MSG)
        if GIT_SEQ_EDITOR_RE.match(command):
            block(GIT_SEQ_EDITOR_MSG)

    elif tool in ("Edit", "Write"):
        path = inp.get("file_path", "")
        text = inp.get("new_string") or inp.get("content", "")
        if SKILL_PATH_RE.search(path) and EVAL_IN_SKILLS_RE.search(text):
            block(EVAL_MSG)

    sys.exit(0)


if __name__ == "__main__":
    main()
