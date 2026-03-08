#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp>=1.0"]
# ///

"""MCP server for Git operations."""

import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Add lib directory to path for imports
lib_path = Path(__file__).parent / "lib"
import sys

sys.path.insert(0, str(lib_path))
from subprocess_utils import run_script, parse_key_value_output

server = FastMCP(name="dev10x-git")


@server.tool()
async def push_safe(
    args: list[str],
    protected_branches: list[str] | None = None,
) -> dict:
    """Safely push git branches with protection for main/develop.

    Args:
        args: Arguments to pass to git push (e.g., ["origin", "branch-name"])
        protected_branches: List of branch names to protect (default: main, develop)

    Returns:
        Dictionary with keys: success (bool), branch, remote, blocked_reason (if blocked)
    """
    # Build command: script args + optional protected branches
    cmd_args = list(args)
    if protected_branches:
        for pb in protected_branches:
            cmd_args.extend(["--protected", pb])

    result = run_script("skills/git/scripts/git-push-safe.sh", *cmd_args)

    if result.returncode != 0:
        return {"success": False, "error": result.stderr.strip()}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return parse_key_value_output(result.stdout)


@server.tool()
async def rebase_groom(
    seq_path: str,
    base_ref: str,
) -> dict:
    """Rebase and groom commits using an interactive sequence file.

    Args:
        seq_path: Path to git rebase sequence file
        base_ref: Base ref to rebase onto (e.g., develop, main)

    Returns:
        Dictionary with keys: success (bool), commits_rewritten (int)
    """
    result = run_script("skills/git/scripts/git-rebase-groom.sh", seq_path, base_ref)

    if result.returncode != 0:
        return {"success": False, "error": result.stderr.strip()}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return parse_key_value_output(result.stdout)


@server.tool()
async def create_worktree(
    branch: str,
    base: str | None = None,
    path: str | None = None,
) -> dict:
    """Create a new git worktree.

    Args:
        branch: Branch name for the worktree
        base: Base ref to create from (default: develop)
        path: Worktree path (default: ../.worktrees/{project}-NN)

    Returns:
        Dictionary with keys: worktree_path, branch, created (bool)
    """
    args = [branch]

    if base is not None:
        args.extend(["--base", base])
    if path is not None:
        args.extend(["--path", path])

    result = run_script("skills/git-worktree/scripts/create-worktree.sh", *args)

    if result.returncode != 0:
        return {"created": False, "error": result.stderr.strip()}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return parse_key_value_output(result.stdout)


if __name__ == "__main__":
    server.run()
