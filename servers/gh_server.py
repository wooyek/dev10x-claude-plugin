#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp>=1.0"]
# ///

"""MCP server for GitHub operations."""

import json
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Add lib directory to path for imports
lib_path = Path(__file__).parent / "lib"
import sys

sys.path.insert(0, str(lib_path))
from subprocess_utils import run_script, parse_key_value_output

server = FastMCP(name="dev10x-gh")


@server.tool()
async def detect_tracker(ticket_id: str) -> dict:
    """Detect issue tracker type from a ticket ID.

    Args:
        ticket_id: Ticket identifier (e.g., GH-15, TEAM-133, TT-42)

    Returns:
        Dictionary with keys: tracker, ticket_id, ticket_number, fixes_url
    """
    result = run_script("skills/gh-context/scripts/detect-tracker.sh", ticket_id)

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return parse_key_value_output(result.stdout)


@server.tool()
async def pr_detect(
    arg: str,
) -> dict:
    """Detect PR context from a PR number, URL, or branch name.

    Args:
        arg: PR number (#123), full URL, or branch name

    Returns:
        Dictionary with keys: pr_number, repo, branch, state, head_ref
    """
    result = run_script("skills/gh-context/scripts/gh-pr-detect.sh", arg)

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return parse_key_value_output(result.stdout)


@server.tool()
async def issue_get(
    number: int,
    repo: str | None = None,
) -> dict:
    """Get GitHub issue details.

    Args:
        number: Issue number
        repo: Repository (owner/repo). If omitted, uses current repo

    Returns:
        Dictionary with keys: title, state, body, labels, linked_prs
    """
    args = [str(number)]
    if repo:
        args.extend(["--repo", repo])

    result = run_script("skills/gh-context/scripts/gh-issue-get.sh", *args)

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    # Try parsing as JSON first (if the script returns JSON output)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        # Fall back to key-value parsing
        return parse_key_value_output(result.stdout)


@server.tool()
async def issue_comments(
    number: int,
    repo: str | None = None,
) -> dict:
    """Get GitHub issue comments.

    Args:
        number: Issue number
        repo: Repository (owner/repo). If omitted, uses current repo

    Returns:
        Dictionary with key: comments (list of comment objects)
    """
    args = [str(number)]
    if repo:
        args.extend(["--repo", repo])

    result = run_script("skills/gh-context/scripts/gh-issue-comments.sh", *args)

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    # Try parsing as JSON
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        # Return raw stdout if not JSON
        return {"raw_output": result.stdout}


@server.tool()
async def pr_comments(
    action: str,
    pr_number: int | None = None,
    comment_id: int | None = None,
    body: str | None = None,
    repo: str | None = None,
) -> dict:
    """Manage GitHub PR comments (list, create, update, delete).

    Args:
        action: One of: list, create, update, delete
        pr_number: PR number (required for list, create, update/delete by ID)
        comment_id: Comment ID (required for update/delete operations)
        body: Comment body text (required for create action)
        repo: Repository (owner/repo). If omitted, uses current repo

    Returns:
        Dictionary with action results (comments list or operation status)
    """
    home = Path.home()
    tool_path = home / ".claude" / "tools" / "gh-pr-comments.py"

    if not tool_path.exists():
        return {"error": f"Tool not found: {tool_path}"}

    args = [str(tool_path), action]

    if pr_number is not None:
        args.extend(["--pr-number", str(pr_number)])
    if comment_id is not None:
        args.extend(["--comment-id", str(comment_id)])
    if body is not None:
        args.extend(["--body", body])
    if repo is not None:
        args.extend(["--repo", repo])

    result = subprocess.run(args, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw_output": result.stdout}


@server.tool()
async def request_review(
    pr_number: int,
    reviewers: list[str],
    team: bool | None = None,
    repo: str | None = None,
) -> dict:
    """Request review on a GitHub PR from users or teams.

    Args:
        pr_number: PR number
        reviewers: List of reviewer usernames or team names
        team: Whether reviewers are teams (vs users)
        repo: Repository (owner/repo). If omitted, uses current repo

    Returns:
        Dictionary with keys: requested (list), failed (list)
    """
    home = Path.home()
    tool_path = home / ".claude" / "tools" / "gh-request-review.py"

    if not tool_path.exists():
        return {"error": f"Tool not found: {tool_path}"}

    args = [str(tool_path), str(pr_number)]
    args.extend(reviewers)

    if team:
        args.append("--team")
    if repo is not None:
        args.extend(["--repo", repo])

    result = subprocess.run(args, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw_output": result.stdout}


if __name__ == "__main__":
    server.run()
