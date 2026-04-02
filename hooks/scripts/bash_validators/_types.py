"""Thin re-export shim — delegates to dev10x.domain.hook_input."""

import sys

import dev10x.domain.hook_input as _real

sys.modules[__name__] = _real
