"""Validator: redirect raw CLI commands to their skill/tool equivalents.

Loads validation rules from command-skill-map.yaml at module level.
Only processes rules where matcher=Bash and hook_block=true.

Supports three friction levels:

  strict   — hard deny (exit 2), no fallback shown
  guided   — hard deny + fallback instructions in systemMessage (default)
  adaptive — allow + warning in additionalContext (future)

The YAML is the single source of truth shared with
Dev10x:skill-reinforcement. Per-project overrides:
  ~/.claude/projects/<project>/memory/playbooks/skill-reinforcement.yaml
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from bash_validators._types import HookInput, HookResult

_YAML_PATH = Path(__file__).parent / "command-skill-map.yaml"

SKIP_ENV_VAR = "DEV10X_SKIP_CMD_VALIDATION"

SKIP_PREFIX_RE = re.compile(rf"^{SKIP_ENV_VAR}=(true|1)\s+", re.IGNORECASE)

OVERRIDE_HINT = (
    "\n\nTo force this command (e.g., from inside a skill that "
    "legitimately needs it), prefix it with:\n"
    f"  {SKIP_ENV_VAR}=true <command>"
)


@dataclass
class _Compensation:
    type: str
    skill: str = ""
    tool: str = ""
    guardrails: str = ""
    fallback: str = ""
    description: str = ""


@dataclass
class _Rule:
    name: str
    patterns: list[re.Pattern[str]]
    except_: list[str]
    compensations: list[_Compensation]


@dataclass
class _Config:
    friction_level: str = "guided"
    plugin_repo: str = ""
    rules: list[_Rule] = field(default_factory=list)


def _load_config(yaml_path: Path = _YAML_PATH) -> _Config:
    data: dict[str, Any] = yaml.safe_load(yaml_path.read_text())
    cfg_data = data.get("config", {})
    friction_level = cfg_data.get("friction_level", "guided")
    plugin_repo = cfg_data.get("plugin_repo", "")
    rules: list[_Rule] = []
    for entry in data.get("rules", []):
        matcher = entry.get("matcher", "Bash")
        if matcher != "Bash":
            continue
        if not entry.get("hook_block", False):
            continue
        compensations = [
            _Compensation(
                type=c.get("type", "use-skill"),
                skill=c.get("skill", ""),
                tool=c.get("tool", ""),
                guardrails=c.get("guardrails", ""),
                fallback=c.get("fallback", "").strip(),
                description=c.get("description", "").strip(),
            )
            for c in entry.get("compensations", [])
        ]
        rules.append(
            _Rule(
                name=entry.get("name", ""),
                patterns=[re.compile(p) for p in entry.get("patterns", [])],
                except_=entry.get("except", []),
                compensations=compensations,
            )
        )
    return _Config(
        friction_level=friction_level,
        plugin_repo=plugin_repo,
        rules=rules,
    )


_CONFIG: _Config = _load_config()

_QUICK_TOKENS = frozenset(["commit", "create", "push", "rebase", "checks", "issue"])

_COMMIT_HEAL_MSG = (
    "\u26d4  `git commit` blocked — wrong temp file path.\n\n"
    "The `-F` path must be under `/tmp/claude/git/`.\n"
    "Create it with: `mcp__plugin_Dev10x_cli__mktmp("
    'namespace="git", prefix="commit-msg", ext=".txt")`\n'
    "then: `git commit -F <returned-path>`\n\n"
    "If you used a different namespace (e.g. `commit` instead of "
    "`git`), that is why this was blocked."
)

_SKILL_COMMIT_FILE_RE = re.compile(r"-F\s+/tmp/claude/git/\S+")
_WRONG_TEMP_PATH_RE = re.compile(r"-F\s+/tmp/claude/(?!git/)\S+/\S+\.\S+")


def _format_skill_msg(
    *,
    label: str,
    comp: _Compensation,
    friction_level: str,
    plugin_repo: str,
) -> str:
    file_issue_hint = (
        f"\n\nIf you are inside a skill that instructed this command, "
        f"file an issue at {plugin_repo} — the skill needs updating."
        if plugin_repo
        else ""
    )
    if comp.type == "use-tool":
        if friction_level == "guided" and comp.description:
            return (
                f"\u26d4  `{label}` blocked — use the MCP tool instead.\n\n"
                f"  Tool: `{comp.tool}`\n\n"
                f"Why: Raw CLI bypasses structured responses and causes\n"
                f"permission friction ({comp.guardrails}).\n\n"
                f"If the MCP server is unavailable, fall back to:\n"
                f"{comp.description}{file_issue_hint}{OVERRIDE_HINT}"
            )
        return (
            f"\u26d4  `{label}` blocked — use the MCP tool instead.\n\n"
            f"  Tool: `{comp.tool}`\n\n"
            f"Why: Raw CLI bypasses structured responses and causes\n"
            f"permission friction ({comp.guardrails}).{file_issue_hint}{OVERRIDE_HINT}"
        )

    if friction_level == "guided" and comp.fallback:
        return (
            f"\u26d4  `{label}` blocked — use the skill instead.\n\n"
            f"  Skill: `Skill({comp.skill})`\n\n"
            f"Why: Raw CLI bypasses guardrails that the skill enforces\n"
            f"({comp.guardrails}).\n\n"
            f"If the skill fails, apply these guardrails manually:\n"
            f"{comp.fallback}{file_issue_hint}{OVERRIDE_HINT}"
        )
    return (
        f"\u26d4  `{label}` blocked — use the skill instead.\n\n"
        f"  Skill: `Skill({comp.skill})`\n\n"
        f"Why: Raw CLI bypasses guardrails that the skill enforces\n"
        f"({comp.guardrails}).{file_issue_hint}{OVERRIDE_HINT}"
    )


@dataclass
class SkillRedirectValidator:
    name: str = "skill-redirect"

    def should_run(self, inp: HookInput) -> bool:
        if SKIP_PREFIX_RE.match(inp.command):
            return False
        cmd_lower = inp.command.lower()
        return any(token in cmd_lower for token in _QUICK_TOKENS)

    def validate(self, inp: HookInput) -> HookResult | None:
        command = inp.command
        for rule in _CONFIG.rules:
            if not any(p.search(command) for p in rule.patterns):
                continue
            if any(exc in command for exc in rule.except_):
                continue
            comp = rule.compensations[0] if rule.compensations else None
            if not comp:
                continue
            if comp.skill == "Dev10x:git-commit" and _SKILL_COMMIT_FILE_RE.search(command):
                continue
            if comp.skill == "Dev10x:git-commit" and _WRONG_TEMP_PATH_RE.search(command):
                return HookResult(message=_COMMIT_HEAL_MSG)
            label = rule.patterns[0].pattern
            msg = _format_skill_msg(
                label=label,
                comp=comp,
                friction_level=_CONFIG.friction_level,
                plugin_repo=_CONFIG.plugin_repo,
            )
            return HookResult(message=msg)
        return None
