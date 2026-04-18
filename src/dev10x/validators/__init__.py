"""Bash command validators for Claude Code PreToolUse hooks.

Single-dispatcher architecture: one Python process validates all Bash
commands by iterating a registry of Validator implementations. Each
validator has a fast `should_run` predicate and a `validate` method.

Ordering matters: allow-validators run before deny-validators so safe
patterns get auto-approved before a deny-validator would block them.

Validators are lazily imported — only loaded when the registry is
first accessed via get_validators(). This avoids paying the import
cost of all 8 modules at module-level on every hook invocation.

Profile filtering (GH-413): validators declare a profile tier
("minimal", "standard", "strict") and a stable rule_id. The registry
filters the active set based on DEV10X_HOOK_PROFILE (default:
"standard"), DEV10X_HOOK_DISABLE (comma-separated rule_ids), and
DEV10X_HOOK_EXPERIMENTAL (opt-in flag for experimental validators).
"""

from __future__ import annotations

import importlib
import os
from typing import TYPE_CHECKING

from dev10x.validators.base import PROFILE_HIERARCHY

if TYPE_CHECKING:
    from dev10x.validators.base import Validator

_VALIDATOR_SPECS: list[tuple[str, str, str, str, bool]] = [
    # (module_path, class_name, rule_id, profile, experimental)
    ("dev10x.validators.safe_subshell", "SafeSubshellValidator", "DX001", "minimal", False),
    (
        "dev10x.validators.command_substitution",
        "CommandSubstitutionValidator",
        "DX002",
        "minimal",
        False,
    ),
    ("dev10x.validators.execution_safety", "ExecutionSafetyValidator", "DX003", "minimal", False),
    ("dev10x.validators.sql_safety", "SqlSafetyValidator", "DX004", "minimal", False),
    ("dev10x.validators.pr_base", "PrBaseValidator", "DX005", "minimal", False),
    ("dev10x.validators.skill_redirect", "SkillRedirectValidator", "DX006", "standard", False),
    ("dev10x.validators.prefix_friction", "PrefixFrictionValidator", "DX007", "standard", False),
    ("dev10x.validators.commit_jtbd", "CommitJtbdValidator", "DX008", "strict", False),
]

_DEFAULT_PROFILE = "standard"


def _profile_includes(*, validator_profile: str, active_profile: str) -> bool:
    """Return True if validator runs at the active profile level.

    Lower-tier validators run at all higher tiers. Unknown profiles
    default to "standard".
    """
    try:
        validator_tier = PROFILE_HIERARCHY.index(validator_profile)
        active_tier = PROFILE_HIERARCHY.index(active_profile)
    except ValueError:
        validator_tier = PROFILE_HIERARCHY.index(_DEFAULT_PROFILE)
        active_tier = PROFILE_HIERARCHY.index(_DEFAULT_PROFILE)
    return validator_tier <= active_tier


def _load_profile_config() -> tuple[str, set[str], bool]:
    """Read profile configuration from environment variables.

    Returns:
        (active_profile, disabled_rule_ids, experimental_enabled)
    """
    active = os.environ.get("DEV10X_HOOK_PROFILE", _DEFAULT_PROFILE).strip().lower()
    if active not in PROFILE_HIERARCHY:
        active = _DEFAULT_PROFILE

    disabled_raw = os.environ.get("DEV10X_HOOK_DISABLE", "")
    disabled = {rid.strip().upper() for rid in disabled_raw.split(",") if rid.strip()}

    experimental_raw = os.environ.get("DEV10X_HOOK_EXPERIMENTAL", "").strip().lower()
    experimental_enabled = experimental_raw in ("1", "true", "yes", "on")

    return active, disabled, experimental_enabled


_validators: list[Validator] | None = None


def get_validators() -> list[Validator]:
    global _validators
    if _validators is None:
        from dev10x.validators.base import Validator as V

        active_profile, disabled, experimental_enabled = _load_profile_config()
        _validators = []
        for module_path, class_name, rule_id, profile, experimental in _VALIDATOR_SPECS:
            if rule_id.upper() in disabled:
                continue
            if experimental and not experimental_enabled:
                continue
            if not _profile_includes(validator_profile=profile, active_profile=active_profile):
                continue
            mod = importlib.import_module(module_path)
            cls = getattr(mod, class_name)
            instance = cls()
            if not hasattr(instance, "rule_id"):
                instance.rule_id = rule_id
            if not hasattr(instance, "profile"):
                instance.profile = profile
            if not hasattr(instance, "experimental"):
                instance.experimental = experimental
            assert isinstance(instance, V), f"{class_name} does not implement Validator"
            _validators.append(instance)
    return _validators


def reset_registry() -> None:
    """Clear the cached validator registry — used by tests."""
    global _validators
    _validators = None


__all__ = ["get_validators", "reset_registry"]
