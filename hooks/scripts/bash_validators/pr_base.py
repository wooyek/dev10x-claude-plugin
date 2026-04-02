"""Thin re-export shim — delegates to dev10x.validators.pr_base.

Replaces itself in sys.modules so that mock.patch targets the real module.
"""

import sys

import dev10x.validators.pr_base as _real

sys.modules[__name__] = _real
