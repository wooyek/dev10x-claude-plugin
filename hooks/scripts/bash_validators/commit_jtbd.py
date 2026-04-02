"""Thin re-export shim — delegates to dev10x.validators.commit_jtbd."""

import sys

import dev10x.validators.commit_jtbd as _real

sys.modules[__name__] = _real
