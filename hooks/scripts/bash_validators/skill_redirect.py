"""Validator: redirect raw CLI commands to their skill equivalents.

Loads command-to-skill mappings from command-skill-map.yaml at module
level. Supports three friction levels:

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

_STRICT_MSG = (
    "\u26d4  `{command}` blocked — use the skill instead.\n\n"
    "  Skill: `Skill({skill})`\n\n"
    "Why: Raw CLI bypasses guardrails that the skill enforces\n"
    "({guardrails}).\n\n"
    "If you are inside the skill already, this is a bug — "
    "file it at https://github.com/Brave-Labs/Dev10x/issues"
)

_GUIDED_MSG = (
    "\u26d4  `{command}` blocked — use the skill instead.\n\n"
    "  Skill: `Skill({skill})`\n\n"
    "Why: Raw CLI bypasses guardrails that the skill enforces\n"
    "({guardrails}).\n\n"
    "If the skill fails, apply these guardrails manually:\n"
    "{fallback_instructions}\n\n"
    "If you are inside the skill already, this is a bug — "
    "file it at https://github.com/Brave-Labs/Dev10x/issues"
)

_MCP_STRICT_MSG = (
    "\u26d4  `{command}` blocked — use the MCP tool instead.\n\n"
    "  Tool: `{skill}`\n\n"
    "Why: Raw CLI bypasses structured responses and causes\n"
    "permission friction ({guardrails}).\n\n"
    "If the MCP server is unavailable, this is a bug — "
    "file it at https://github.com/Brave-Labs/Dev10x/issues"
)

_MCP_GUIDED_MSG = (
    "\u26d4  `{command}` blocked — use the MCP tool instead.\n\n"
    "  Tool: `{skill}`\n\n"
    "Why: Raw CLI bypasses structured responses and causes\n"
    "permission friction ({guardrails}).\n\n"
    "If the MCP server is unavailable, fall back to:\n"
    "{fallback_instructions}"
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

_SKILL_COMMIT_FILE_RE = re.compile(r"-F\s+/tmp/claude/git/\S+")
_WRONG_TEMP_PATH_RE = re.compile(r"-F\s+/tmp/claude/(?!git/)\S+/\S+\.\S+")


@dataclass
class _Mapping:
    skill: str
    patterns: list[re.Pattern[str]]
    hook_block: bool
    hook_except: list[str]
    guardrails: str
    fallback_instructions: str
    type: str = "skill"


@dataclass
class _MapConfig:
    friction_level: str = "guided"
    mappings: list[_Mapping] = field(default_factory=list)


def _load_config(yaml_path: Path = _YAML_PATH) -> _MapConfig:
    data: dict[str, Any] = yaml.safe_load(yaml_path.read_text())
    cfg_data = data.get("config", {})
    friction_level = cfg_data.get("friction_level", "guided")
    mappings: list[_Mapping] = []
    for entry in data.get("mappings", []):
        if not entry.get("hook_block", False):
            continue
        mappings.append(
            _Mapping(
                skill=entry["skill"],
                patterns=[re.compile(p) for p in entry.get("patterns", [])],
                hook_block=True,
                hook_except=entry.get("hook_except", []),
                guardrails=entry.get("guardrails", ""),
                fallback_instructions=entry.get("fallback_instructions", "").strip(),
                type=entry.get("type", "skill"),
            )
        )
    return _MapConfig(friction_level=friction_level, mappings=mappings)


_CONFIG: _MapConfig = _load_config()

_QUICK_TOKENS = frozenset(["commit", "create", "push", "rebase", "checks", "issue"])


@dataclass
class SkillRedirectValidator:
    name: str = "skill-redirect"

    def should_run(self, inp: HookInput) -> bool:
        cmd_lower = inp.command.lower()
        return any(token in cmd_lower for token in _QUICK_TOKENS)

    def validate(self, inp: HookInput) -> HookResult | None:
        command = inp.command
        for mapping in _CONFIG.mappings:
            if not any(p.search(command) for p in mapping.patterns):
                continue
            if any(exc in command for exc in mapping.hook_except):
                continue
            if mapping.skill == "Dev10x:git-commit" and _SKILL_COMMIT_FILE_RE.search(command):
                continue
            if mapping.skill == "Dev10x:git-commit" and _WRONG_TEMP_PATH_RE.search(command):
                return HookResult(message=_COMMIT_HEAL_MSG)
            label = mapping.patterns[0].pattern
            if mapping.type == "mcp":
                strict_tpl, guided_tpl = _MCP_STRICT_MSG, _MCP_GUIDED_MSG
            else:
                strict_tpl, guided_tpl = _STRICT_MSG, _GUIDED_MSG
            if _CONFIG.friction_level == "guided" and mapping.fallback_instructions:
                msg = guided_tpl.format(
                    command=label,
                    skill=mapping.skill,
                    guardrails=mapping.guardrails,
                    fallback_instructions=mapping.fallback_instructions,
                )
            else:
                msg = strict_tpl.format(
                    command=label,
                    skill=mapping.skill,
                    guardrails=mapping.guardrails,
                )
            return HookResult(message=msg)
        return None
