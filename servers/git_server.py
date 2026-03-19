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
from subprocess_utils import parse_key_value_output, run_script

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


@server.tool()
async def mass_rewrite(
    config_path: str,
) -> dict:
    """Rewrite multiple commit messages in one unattended rebase pass.

    Args:
        config_path: Path to JSON config file with rewrite instructions.
            Config format: {"base": "develop", "commits": {"sha": "new msg", ...}}

    Returns:
        Dictionary with keys: success (bool), output (str), error (str if failed)
    """
    result = run_script(
        "skills/git-groom/scripts/mass-rewrite.py",
        config_path,
    )

    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr.strip(),
            "output": result.stdout.strip(),
        }

    return {"success": True, "output": result.stdout.strip()}


@server.tool()
async def start_split_rebase(
    commit_hash: str,
    base_branch: str = "develop",
) -> dict:
    """Start an interactive rebase to split a commit into multiple atomic commits.

    Marks the specified commit for editing, then resets it to unstage all
    changes so you can create multiple commits from the original.

    Args:
        commit_hash: The commit hash to split
        base_branch: Base branch for the rebase (default: develop)

    Returns:
        Dictionary with keys: success (bool), output (str), error (str if failed)
    """
    result = run_script(
        "skills/git-commit-split/scripts/start-split-rebase.sh",
        commit_hash,
        base_branch,
    )

    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr.strip(),
            "output": result.stdout.strip(),
        }

    return {"success": True, "output": result.stdout.strip()}


@server.tool()
async def next_worktree_name(
    base_dir: str | None = None,
) -> dict:
    """Calculate the next available worktree path.

    Finds the highest existing worktree number for the current project
    and returns the next incremented path.

    Args:
        base_dir: Override worktrees parent directory (default: ../.worktrees)

    Returns:
        Dictionary with keys: path (str)
    """
    args = [base_dir] if base_dir else []

    result = run_script(
        "skills/git-worktree/scripts/next-worktree-name.sh",
        *args,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return {"path": result.stdout.strip()}


@server.tool()
async def setup_aliases() -> dict:
    """Set up global git aliases for branch comparison operations.

    Configures aliases like git develop-log, git develop-diff, git develop-rebase
    that wrap $(git merge-base ...) subshells into stable command prefixes.
    Idempotent — safe to call multiple times.

    Returns:
        Dictionary with keys: success (bool), output (str)
    """
    result = run_script(
        "skills/git-alias-setup/scripts/git-alias-setup.sh",
    )

    if result.returncode != 0:
        return {"success": False, "error": result.stderr.strip()}

    return {"success": True, "output": result.stdout.strip()}


if __name__ == "__main__":
    server.run()
