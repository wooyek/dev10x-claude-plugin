"""Thin re-export shim — delegates to dev10x.validators.

This package is kept during migration so existing hook entry points
(validate-bash-command.py) continue to work without path changes.
Remove once all consumers import from dev10x.validators directly.
"""

from dev10x.validators import VALIDATORS, Validator

__all__ = ["VALIDATORS", "Validator"]
