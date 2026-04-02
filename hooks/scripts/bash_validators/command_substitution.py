"""Thin re-export shim — delegates to dev10x.validators.command_substitution."""

import sys

import dev10x.validators.command_substitution as _real

sys.modules[__name__] = _real
