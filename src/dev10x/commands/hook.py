from __future__ import annotations

import os
import sys
import traceback

import click

from dev10x.domain import HookInput
from dev10x.validators import VALIDATORS

_DEBUG = os.environ.get("HOOK_DEBUG", "") != ""


@click.group()
def hook() -> None:
    """Hook entry points (validate-bash, validate-edit, plan-sync, session)."""


@hook.command(name="validate-bash")
def validate_bash() -> None:
    """Validate Bash commands via the unified validator registry.

    Reads JSON from stdin, dispatches to registered validators.
    Exit codes: 0=allow, 2=block.
    """
    inp = HookInput.from_stdin()
    if inp.tool_name != "Bash":
        sys.exit(0)
    if not inp.command:
        sys.exit(0)

    for validator in VALIDATORS:
        try:
            if validator.should_run(inp=inp):
                result = validator.validate(inp=inp)
                if result is not None:
                    result.emit()
        except Exception:
            if _DEBUG:
                print(
                    f"[HOOK_DEBUG] {validator.name} raised:",
                    file=sys.stderr,
                )
                traceback.print_exc(file=sys.stderr)
            continue

    sys.exit(0)
