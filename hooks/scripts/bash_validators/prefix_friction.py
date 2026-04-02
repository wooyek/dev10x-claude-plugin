"""Thin re-export shim — delegates to dev10x.validators.prefix_friction."""

import sys

import dev10x.validators.prefix_friction as _real

sys.modules[__name__] = _real
