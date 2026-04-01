#!/usr/bin/env python3
"""PreToolUse hook: unified Edit|Write validator.

Single dispatcher that replaces validate-edit-security.py and
block-sensitive-file-write.py. Loads rules from command-skill-map.yaml
where matcher="Edit|Write", iterates registered rules, first block wins.

Exit codes: 0=allow, 2=block
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import click
import yaml

_YAML_PATH = Path(__file__).parent / "bash_validators" / "command-skill-map.yaml"


@dataclass(frozen=True)
class _Rule:
    name: str
    file_pattern: re.Pattern[str] | None
    file_names: frozenset[str]
    file_prefixes: tuple[str, ...]
    file_substrings: tuple[str, ...]
    content_pattern: re.Pattern[str] | None
    message: str
    compensations: list[dict[str, str]] = field(default_factory=list)


def _load_rules(yaml_path: Path = _YAML_PATH) -> list[_Rule]:
    data: dict[str, Any] = yaml.safe_load(yaml_path.read_text())
    rules: list[_Rule] = []
    for entry in data.get("rules", []):
        if entry.get("matcher") != "Edit|Write":
            continue
        if not entry.get("hook_block", False):
            continue
        fp = entry.get("file_pattern")
        cp = entry.get("content_pattern")
        rules.append(
            _Rule(
                name=entry.get("name", ""),
                file_pattern=re.compile(fp) if fp else None,
                file_names=frozenset(entry.get("file_names", [])),
                file_prefixes=tuple(entry.get("file_prefixes", [])),
                file_substrings=tuple(entry.get("file_substrings", [])),
                content_pattern=re.compile(cp) if cp else None,
                message=(entry.get("message") or entry.get("reason") or "BLOCKED").strip(),
                compensations=entry.get("compensations", []),
            )
        )
    return rules


def _basename(path: str) -> str:
    return path.rsplit("/", 1)[-1] if "/" in path else path


def _matches_file(rule: _Rule, file_path: str) -> bool:
    if rule.file_pattern and rule.file_pattern.search(file_path):
        return True
    name = _basename(file_path)
    if name in rule.file_names:
        return True
    if any(name.startswith(p) for p in rule.file_prefixes):
        return True
    if any(s in file_path for s in rule.file_substrings):
        return True
    return False


def _matches_content(rule: _Rule, content: str) -> bool:
    if rule.content_pattern is None:
        return True
    return rule.content_pattern.search(content) is not None


def _format_message(rule: _Rule, file_path: str) -> str:
    msg = rule.message.format(file_path=file_path)
    for comp in rule.compensations:
        desc = comp.get("description", "")
        if desc:
            msg += f"\n\n{desc.strip()}"
    return msg


def _block(message: str) -> None:
    result = {
        "hookSpecificOutput": {"permissionDecision": "deny"},
        "systemMessage": message,
    }
    print(json.dumps(result), file=sys.stderr)
    sys.exit(2)


@click.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to validation rules YAML (default: command-skill-map.yaml)",
)
@click.option("--debug", is_flag=True, help="Print debug info to stderr")
def main(config_path: Path | None, debug: bool) -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool = data.get("tool_name", "")
    if tool not in ("Edit", "Write"):
        sys.exit(0)

    inp = data.get("tool_input", {})
    file_path = inp.get("file_path", "")
    content = inp.get("new_string") or inp.get("content", "")

    yaml_path = config_path or _YAML_PATH
    rules = _load_rules(yaml_path=yaml_path)

    if debug:
        print(f"[DEBUG] Loaded {len(rules)} Edit|Write rules", file=sys.stderr)

    for rule in rules:
        if not _matches_file(rule=rule, file_path=file_path):
            continue
        if not _matches_content(rule=rule, content=content):
            continue
        if debug:
            print(f"[DEBUG] Rule '{rule.name}' matched: {file_path}", file=sys.stderr)
        _block(message=_format_message(rule=rule, file_path=file_path))

    sys.exit(0)


if __name__ == "__main__":
    main()
