"""Thin re-export shim — delegates to dev10x.validators.skill_redirect.

Replaces itself in sys.modules so that `import bash_validators.skill_redirect`
returns the real module. This ensures module-level state mutations in tests
(e.g., `mod._CONFIG = ...`) affect the actual module, not a proxy.
"""

import sys

import dev10x.validators.skill_redirect as _real

sys.modules[__name__] = _real
