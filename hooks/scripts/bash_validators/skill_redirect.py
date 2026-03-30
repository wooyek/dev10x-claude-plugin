"""Validator: redirect raw CLI commands to their skill equivalents.

Blocks Bash commands that bypass skill guardrails (gitmoji, JTBD,
CI monitoring, protected branch checks) by auto-denying with a
systemMessage pointing to the correct skill.

Blocked patterns:
  - git commit     → Dev10x:git-commit  (except --fixup, --amend,
    and -F with skill temp paths /tmp/claude/git/*)
  - gh pr create   → Dev10x:gh-pr-create (skill uses MCP create_pr)
  - git push       → Dev10x:git          (skill uses MCP push_safe)
  - git rebase -i  → Dev10x:git-groom    (skill uses MCP rebase_groom)
  - gh pr checks --watch → Dev10x:gh-pr-monitor (skill uses MCP tools)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from bash_validators._types import HookInput, HookResult

_REDIRECT_MSG = (
    "\u26d4  `{command}` blocked — use the skill instead.\n\n"
    "  Skill: `Skill({skill})`\n\n"
    "Why: Raw CLI bypasses guardrails that the skill enforces\n"
    "({guardrails}).\n\n"
    "If you are inside the skill already, this is a bug — "
    "file it at https://github.com/Brave-Labs/Dev10x/issues"
)

_COMMIT_HEAL_MSG = (
    "\u26d4  `git commit` blocked — wrong temp file path.\n\n"
    "The `-F` path must be under `/tmp/claude/git/`.\n"
    "Create it with: `mcp__plugin_Dev10x_cli__mktmp("
    'namespace="git", prefix="commit-msg", ext=".txt")`\n'
    "then: `git commit -F <returned-path>`\n\n"
    "If you used a different namespace (e.g. `commit` instead of "
    "`git`), that is why this was blocked."
)

GIT_COMMIT_RE = re.compile(r"\bgit\s+commit\b(?!.*(?:--fixup|--amend))")
GH_PR_CREATE_RE = re.compile(r"\bgh\s+pr\s+create\b")
GIT_PUSH_RE = re.compile(r"\bgit\s+push\b")
GIT_REBASE_I_RE = re.compile(r"\bgit\s+rebase\b.*(?:\s-i\b|\s--interactive\b)")
GH_PR_CHECKS_WATCH_RE = re.compile(r"\bgh\s+pr\s+checks\b.*(?:\s--watch\b|\s-w\b)")

_RULES: list[tuple[re.Pattern[str], str, str, str]] = [
    (
        GIT_COMMIT_RE,
        "git commit",
        "Dev10x:git-commit",
        "gitmoji prefix, JTBD outcome title, 72-char limit",
    ),
    (
        GH_PR_CREATE_RE,
        "gh pr create",
        "Dev10x:gh-pr-create",
        "Job Story body, ticket linking, commit list, summary comment",
    ),
    (
        GIT_PUSH_RE,
        "git push",
        "Dev10x:git",
        "protected branch checks, force-push safety",
    ),
    (
        GIT_REBASE_I_RE,
        "git rebase -i",
        "Dev10x:git-groom",
        "atomic commits, convention enforcement, non-interactive rebase",
    ),
    (
        GH_PR_CHECKS_WATCH_RE,
        "gh pr checks --watch",
        "Dev10x:gh-pr-monitor",
        "failure detection, fixup commits, re-monitoring after push",
    ),
]

_QUICK_TOKENS = frozenset(["commit", "create", "push", "rebase", "checks"])


@dataclass
class SkillRedirectValidator:
    name: str = "skill-redirect"

    def should_run(self, inp: HookInput) -> bool:
        cmd_lower = inp.command.lower()
        return any(token in cmd_lower for token in _QUICK_TOKENS)

    def validate(self, inp: HookInput) -> HookResult | None:
        command = inp.command
        for pattern, label, skill, guardrails in _RULES:
            if pattern.search(command):
                if label == "git commit":
                    if not _is_direct_commit(command=command):
                        continue
                    if _has_wrong_temp_path(command=command):
                        return HookResult(message=_COMMIT_HEAL_MSG)
                return HookResult(
                    message=_REDIRECT_MSG.format(
                        command=label,
                        skill=skill,
                        guardrails=guardrails,
                    ),
                )
        return None


_SKILL_COMMIT_FILE_RE = re.compile(r"-F\s+/tmp/claude/git/\S+\.[A-Za-z0-9]{12}\.\S+")
_ANY_TEMP_FILE_RE = re.compile(r"-F\s+/tmp/claude/(?!git/)\S+/\S+\.\S+")


def _is_direct_commit(*, command: str) -> bool:
    """Return True unless using -F with a skill-generated temp file.

    The Dev10x:git-commit skill creates commit messages via mktmp
    with namespace=git. Any file under /tmp/claude/git/ is a
    skill-managed temp file and should be allowed through.
    """
    if _SKILL_COMMIT_FILE_RE.search(command):
        return False
    return True


def _has_wrong_temp_path(*, command: str) -> bool:
    """Return True when -F references a /tmp/claude/ path outside /tmp/claude/git/.

    Detects the common mistake of using the wrong mktmp namespace
    (e.g. namespace=commit instead of namespace=git).
    """
    return bool(_ANY_TEMP_FILE_RE.search(command))
