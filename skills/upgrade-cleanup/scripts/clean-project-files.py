#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml", "click"]
# ///
"""Thin shim — delegates to dev10x permission clean."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from dev10x.commands.permission import clean

if __name__ == "__main__":
    clean(standalone_mode=True)
