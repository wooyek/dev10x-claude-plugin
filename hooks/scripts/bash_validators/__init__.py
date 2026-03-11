"""Bash command validators for Claude Code PreToolUse hooks.

Single-dispatcher architecture: one Python process validates all Bash
commands by iterating a registry of Validator implementations. Each
validator has a fast `should_run` predicate and a `validate` method.
"""

from __future__ import annotations

from bash_validators._base import Validator
from bash_validators.commit_jtbd import CommitJtbdValidator
from bash_validators.execution_safety import ExecutionSafetyValidator
from bash_validators.pr_base import PrBaseValidator
from bash_validators.prefix_friction import PrefixFrictionValidator
from bash_validators.sql_safety import SqlSafetyValidator

VALIDATORS: list[Validator] = [
    PrefixFrictionValidator(),
    ExecutionSafetyValidator(),
    CommitJtbdValidator(),
    SqlSafetyValidator(),
    PrBaseValidator(),
]

__all__ = ["VALIDATORS", "Validator"]
