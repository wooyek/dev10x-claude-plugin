"""Thin re-export shim — delegates to dev10x.validators.safe_subshell."""

import sys

import dev10x.validators.safe_subshell as _real

sys.modules[__name__] = _real
