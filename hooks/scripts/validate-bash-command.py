#!/usr/bin/env python3
"""PreToolUse hook: unified Bash command validator.

Thin shim that delegates to `dev10x hook validate-bash`.
Kept for backward compatibility with plugin.json hook config.
"""

from dev10x.commands.hook import validate_bash

if __name__ == "__main__":
    validate_bash()
