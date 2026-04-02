"""Thin re-export shim — delegates to dev10x.validators.base."""

import sys

import dev10x.validators.base as _real

sys.modules[__name__] = _real
