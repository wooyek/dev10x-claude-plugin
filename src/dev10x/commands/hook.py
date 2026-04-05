from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

import click

from dev10x.domain import HookInput
from dev10x.validators import get_validators

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

    for validator in get_validators():
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


@hook.group(name="plan")
def plan() -> None:
    """Plan synchronization commands."""


@plan.command(name="sync")
def plan_sync() -> None:
    """Sync task state from stdin (PostToolUse hook mode)."""
    from dev10x.hooks.task_plan_sync import cmd_hook

    cmd_hook()


@plan.command(name="summary")
def plan_summary() -> None:
    """Read plan YAML, output JSON summary."""
    from dev10x.hooks.task_plan_sync import cmd_json_summary

    cmd_json_summary()


@plan.command(name="set-context")
@click.argument("pairs", nargs=-1, required=True)
def plan_set_context(pairs: tuple[str, ...]) -> None:
    """Store plan-level context metadata (K=V pairs, dot-paths supported)."""
    from dev10x.hooks.task_plan_sync import cmd_set_context

    cmd_set_context(args=list(pairs))


@plan.command(name="archive")
def plan_archive() -> None:
    """Archive completed plan to .claude/session/archive/."""
    from dev10x.hooks.task_plan_sync import cmd_archive

    cmd_archive()


@hook.command(name="permission-denied")
def permission_denied() -> None:
    """Handle PermissionDenied events via the validator registry.

    Reads JSON from stdin, dispatches to validators that implement
    correct(). Returns retry=true with corrective guidance when a
    validator recognizes the denied command.
    Exit codes: 0 always (retry decision is in JSON output).
    """
    from dev10x.validators.base import Corrector

    inp = HookInput.from_stdin()
    if not inp.command:
        sys.exit(0)

    for validator in get_validators():
        try:
            if not validator.should_run(inp=inp):
                continue
            if not isinstance(validator, Corrector):
                continue
            result = validator.correct(inp=inp)
            if result is not None:
                result.emit()
        except Exception:
            if _DEBUG:
                print(
                    f"[HOOK_DEBUG] {validator.name} correct() raised:",
                    file=sys.stderr,
                )
                traceback.print_exc(file=sys.stderr)
            continue

    sys.exit(0)


@hook.command(name="validate-edit")
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
)
@click.option("--debug", is_flag=True)
def validate_edit(config_path: Path | None, debug: bool) -> None:
    """Validate Edit/Write tool calls against sensitive file rules.

    Reads JSON from stdin, checks file paths against rules.
    Exit codes: 0=allow, 2=block.
    """
    import json

    from dev10x.hooks.edit_validator import validate_edit_write

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    validate_edit_write(
        data=data,
        yaml_path=config_path,
        debug=debug,
    )


@hook.group(name="session")
def session() -> None:
    """Session lifecycle commands."""


@session.command(name="reload")
def session_reload_cmd() -> None:
    """Reload prior session state (SessionStart hook)."""
    from dev10x.hooks.session import session_reload

    session_reload()


@session.command(name="compact")
def session_compact_cmd() -> None:
    """Inject context summary before compaction (PreCompact hook)."""
    from dev10x.hooks.session import context_compact

    context_compact()
