from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Compensation:
    type: str
    skill: str = ""
    tool: str = ""
    alias: str = ""
    guardrails: str = ""
    fallback: str = ""
    description: str = ""


@dataclass(frozen=True)
class Rule:
    name: str
    patterns: list[str]
    matcher: str = "Bash"
    except_: list[str] = field(default_factory=list)
    compensations: list[Compensation] = field(default_factory=list)
    hook_block: bool = True
    reason: str = ""
    related: list[str] = field(default_factory=list)
    file_pattern: str = ""
    file_names: list[str] = field(default_factory=list)
    file_prefixes: list[str] = field(default_factory=list)
    file_substrings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Config:
    friction_level: str = "strict"
    plugin_repo: str = ""
    rules: list[Rule] = field(default_factory=list)
