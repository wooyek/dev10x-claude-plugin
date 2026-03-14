"""Data transfer objects for hook input and validation results."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Any, NoReturn


@dataclass(frozen=True)
class HookInput:
    tool_name: str
    command: str
    raw: dict[str, Any]
    cwd: str = ""

    @classmethod
    def from_stdin(cls) -> HookInput:
        try:
            data = json.load(sys.stdin)
        except (json.JSONDecodeError, EOFError):
            data = {}
        return cls(
            tool_name=data.get("tool_name", ""),
            command=data.get("tool_input", {}).get("command", ""),
            raw=data,
            cwd=os.getcwd(),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HookInput:
        return cls(
            tool_name=data.get("tool_name", ""),
            command=data.get("tool_input", {}).get("command", ""),
            raw=data,
        )


@dataclass(frozen=True)
class HookResult:
    message: str

    def emit(self) -> NoReturn:
        result = {
            "hookSpecificOutput": {"permissionDecision": "deny"},
            "systemMessage": self.message,
        }
        print(json.dumps(result), file=sys.stderr)
        sys.exit(2)
