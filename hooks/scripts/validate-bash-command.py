#!/usr/bin/env python3
"""PreToolUse hook: unified Bash command validator.

Single dispatcher that replaces 7 individual Bash PreToolUse hooks
with one process. Parses JSON once, iterates registered validators,
first block wins.

Exit codes: 0=allow, 2=block
"""

from __future__ import annotations

import os
import sys
import traceback

from bash_validators import VALIDATORS
from bash_validators._types import HookInput

_DEBUG = os.environ.get("HOOK_DEBUG", "") != ""


def main() -> None:
    inp = HookInput.from_stdin()
    if inp.tool_name != "Bash":
        sys.exit(0)
    if not inp.command:
        sys.exit(0)

    for validator in VALIDATORS:
        try:
            if validator.should_run(inp=inp):
                result = validator.validate(inp=inp)
                if result is not None:
                    result.emit()
        except Exception:
            if _DEBUG:
                print(
                    f"[HOOK_DEBUG] {validator.name} raised:",
                    file=sys.stderr,
                )
                traceback.print_exc(file=sys.stderr)
            continue

    sys.exit(0)


if __name__ == "__main__":
    main()
