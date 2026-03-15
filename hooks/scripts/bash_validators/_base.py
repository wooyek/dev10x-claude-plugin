"""Validator protocol for Bash command validation."""

from __future__ import annotations

from typing import Protocol

from bash_validators._types import HookAllow, HookInput, HookResult


class Validator(Protocol):
    name: str

    def should_run(self, inp: HookInput) -> bool:
        """Fast predicate — return False to skip this validator entirely."""
        ...

    def validate(self, inp: HookInput) -> HookResult | HookAllow | None:
        """Return HookResult to block, HookAllow to auto-approve, None for no opinion."""
        ...
