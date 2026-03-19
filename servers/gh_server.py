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
from subprocess_utils import parse_key_value_output, run_script

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


@server.tool()
async def detect_base_branch(
    base: str | None = None,
    force: bool = False,
) -> dict:
    """Detect the correct base branch for PRs in the current repository.

    Prefers develop/development, falls back to main/master/trunk.

    Args:
        base: Explicit base branch override
        force: Skip warning when overriding to non-development base

    Returns:
        Dictionary with keys: base_branch (str), has_develop (bool)
    """
    args: list[str] = []
    if base:
        args.extend(["--base", base])
    if force:
        args.append("--force")

    result = run_script(
        "skills/gh-pr-create/scripts/detect-base-branch.sh",
        *args,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    parsed = parse_key_value_output(result.stdout)
    return {
        "base_branch": parsed.get("BASE_BRANCH", ""),
        "has_develop": bool(parsed.get("DEV_BRANCH", "")),
    }


@server.tool()
async def verify_pr_state(
    force: bool = False,
) -> dict:
    """Verify branch state before creating a PR.

    Checks: not on protected branch, no uncommitted changes,
    commits ahead of base, no merge conflicts, no release-branch leaks.

    Args:
        force: Allow targeting a non-development base branch

    Returns:
        Dictionary with keys: branch_name, issue, base_branch
    """
    args: list[str] = []
    if force:
        args.append("--force")

    result = run_script(
        "skills/gh-pr-create/scripts/verify-state.sh",
        *args,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return parse_key_value_output(result.stdout)


@server.tool()
async def pre_pr_checks(
    base_branch: str | None = None,
) -> dict:
    """Run pre-PR quality checks (ruff, mypy, pytest).

    Skips if diff contains only non-Python files.

    Args:
        base_branch: Base branch for diff comparison. Auto-detected if omitted.

    Returns:
        Dictionary with keys: success (bool), output (str)
    """
    args: list[str] = []
    if base_branch:
        args.append(base_branch)

    result = run_script(
        "skills/gh-pr-create/scripts/pre-pr-checks.sh",
        *args,
    )

    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        **({"error": result.stderr.strip()} if result.returncode != 0 else {}),
    }


@server.tool()
async def create_pr(
    title: str,
    job_story: str,
    issue_id: str,
    fixes_url: str | None = None,
    base_branch: str | None = None,
) -> dict:
    """Create a draft PR with two-pass body generation.

    Pushes branch, creates draft PR with job story and commit list,
    then updates body with linked commit references.

    Args:
        title: PR title
        job_story: JTBD Job Story for the PR body
        issue_id: Ticket ID extracted from branch name
        fixes_url: Issue URL for the Fixes: line
        base_branch: Base branch. Auto-detected if omitted.

    Returns:
        Dictionary with keys: pr_number (int), url (str)
    """
    args = [title, job_story, issue_id]
    args.append(fixes_url or "")
    args.append(base_branch or "")

    result = run_script(
        "skills/gh-pr-create/scripts/create-pr.sh",
        *args,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    lines = result.stdout.strip().split("\n")
    pr_number = lines[-1]
    url = next((l for l in lines if l.startswith("http")), f"PR #{pr_number}")
    return {"pr_number": int(pr_number), "url": url}


@server.tool()
async def generate_commit_list(
    pr_number: int,
    base_branch: str | None = None,
) -> dict:
    """Generate a linked commit list for a PR body.

    Each commit gets a clickable link to the PR's commit view.

    Args:
        pr_number: PR number for commit links
        base_branch: Base branch. Auto-detected if omitted.

    Returns:
        Dictionary with key: commit_list (str)
    """
    args = [str(pr_number)]
    if base_branch:
        args.append(base_branch)

    result = run_script(
        "skills/gh-pr-create/scripts/generate-commit-list.sh",
        *args,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return {"commit_list": result.stdout.strip()}


@server.tool()
async def post_summary_comment(
    issue_id: str,
    summary_text: str,
) -> dict:
    """Post summary + checklist as first PR comment.

    Args:
        issue_id: Ticket ID for checklist substitution
        summary_text: Markdown bullet points (one per line)

    Returns:
        Dictionary with keys: success (bool), output (str)
    """
    result = run_script(
        "skills/gh-pr-create/scripts/post-summary-comment.sh",
        issue_id,
        summary_text,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return {"success": True, "output": result.stdout.strip()}


@server.tool()
async def pr_notify(
    pr_number: int,
    repo: str,
    action: str = "prepare",
    channel: str | None = None,
    message: str | None = None,
    message_file: str | None = None,
    reviewer: str | None = None,
    skip_slack: bool = False,
    skip_reviewers: bool = False,
    skip_checklist: bool = False,
) -> dict:
    """PR notification helper for review requests.

    Two actions:
    - prepare: Fetch PR info, count threads, format Slack message
    - send: Post notification, assign reviewers, update checklist

    Args:
        pr_number: PR number
        repo: GitHub repo (owner/name)
        action: "prepare" or "send"
        channel: Slack channel ID (send only)
        message: Notification message text (send only)
        message_file: Path to message file (send only)
        reviewer: GitHub reviewer to assign (send only)
        skip_slack: Skip Slack notification (send only)
        skip_reviewers: Skip reviewer assignment (send only)
        skip_checklist: Skip checklist update (send only)

    Returns:
        Dictionary with PR info (prepare) or operation results (send)
    """
    plugin_root = Path(__file__).parent.parent
    script_path = plugin_root / "skills" / "gh-pr-monitor" / "scripts" / "pr-notify.py"

    if not script_path.exists():
        return {"error": f"Script not found: {script_path}"}

    args = [
        "uv",
        "run",
        "--script",
        str(script_path),
        action,
        "--pr",
        str(pr_number),
        "--repo",
        repo,
    ]

    if action == "send":
        if channel:
            args.extend(["--channel", channel])
        if message:
            args.extend(["--message", message])
        if message_file:
            args.extend(["--message-file", message_file])
        if reviewer:
            args.extend(["--reviewer", reviewer])
        if skip_slack:
            args.append("--skip-slack")
        if skip_reviewers:
            args.append("--skip-reviewers")
        if skip_checklist:
            args.append("--skip-checklist")

    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    if proc.returncode != 0:
        return {"error": proc.stderr.strip()}

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"success": True, "output": proc.stdout.strip()}


if __name__ == "__main__":
    server.run()
