"""Bash command validators for Claude Code PreToolUse hooks.

Single-dispatcher architecture: one Python process validates all Bash
commands by iterating a registry of Validator implementations. Each
validator has a fast `should_run` predicate and a `validate` method.

Ordering matters: allow-validators run before deny-validators so safe
patterns get auto-approved before a deny-validator would block them.
"""

from __future__ import annotations

from dev10x.validators.base import Validator
from dev10x.validators.command_substitution import CommandSubstitutionValidator
from dev10x.validators.commit_jtbd import CommitJtbdValidator
from dev10x.validators.execution_safety import ExecutionSafetyValidator
from dev10x.validators.pr_base import PrBaseValidator
from dev10x.validators.prefix_friction import PrefixFrictionValidator
from dev10x.validators.safe_subshell import SafeSubshellValidator
from dev10x.validators.skill_redirect import SkillRedirectValidator
from dev10x.validators.sql_safety import SqlSafetyValidator

VALIDATORS: list[Validator] = [
    SafeSubshellValidator(),
    CommandSubstitutionValidator(),
    PrefixFrictionValidator(),
    ExecutionSafetyValidator(),
    SkillRedirectValidator(),
    CommitJtbdValidator(),
    SqlSafetyValidator(),
    PrBaseValidator(),
]

__all__ = ["VALIDATORS", "Validator"]
