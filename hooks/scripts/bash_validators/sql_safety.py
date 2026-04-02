"""Thin re-export shim — delegates to dev10x.validators.sql_safety."""

import sys

import dev10x.validators.sql_safety as _real

sys.modules[__name__] = _real
