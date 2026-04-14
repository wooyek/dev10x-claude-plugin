#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml", "click"]
# ///
"""Thin shim — delegates to dev10x permission merge-worktree."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from dev10x.commands.permission import merge_worktree

if __name__ == "__main__":
    merge_worktree(standalone_mode=True)
