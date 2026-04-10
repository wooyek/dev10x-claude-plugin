"""GitHub MCP tool implementations.

Extracted from cli_server.py — cohesive GitHub API and CLI operations.
Each function takes explicit parameters and returns typed dicts.
All public functions are async to avoid blocking the MCP event loop.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

from dev10x.domain.repository_ref import RepositoryRef
from dev10x.mcp.subprocess_utils import (
    async_run,
    async_run_script,
    parse_key_value_output,
)

if TYPE_CHECKING:
    pass


async def _detect_repo() -> str | None:
    result = await async_run(
        args=["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        timeout=10,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


async def _gh_api(
    endpoint: str,
    *,
    method: str = "GET",
    fields: dict[str, str | int | list[str]] | None = None,
    jq: str | None = None,
) -> subprocess.CompletedProcess[str]:
    args = ["gh", "api"]
    if method != "GET":
        args.extend(["-X", method])
    if jq:
        args.extend(["--jq", jq])
    if fields:
        for key, value in fields.items():
            if isinstance(value, list):
                for item in value:
                    args.extend(["-f", f"{key}[]={item}"])
            elif isinstance(value, int):
                args.extend(["-F", f"{key}={value}"])
            else:
                args.extend(["-f", f"{key}={value}"])
    args.append(endpoint)

    return await async_run(args=args, timeout=30)


async def _resolve_repo(
    repo: str | None,
) -> tuple[RepositoryRef | None, dict[str, str] | None]:
    resolved = repo or await _detect_repo()
    if not resolved:
        return None, {"error": "Could not detect repository. Provide repo parameter."}
    try:
        return RepositoryRef.parse(resolved), None
    except ValueError as exc:
        return None, {"error": str(exc)}


async def detect_tracker(*, ticket_id: str) -> dict[str, Any]:
    result = await async_run_script(
        "skills/gh-context/scripts/detect-tracker.sh",
        ticket_id,
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    return parse_key_value_output(result.stdout)


async def pr_detect(*, arg: str) -> dict[str, Any]:
    result = await async_run_script(
        "skills/gh-context/scripts/gh-pr-detect.sh",
        arg,
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    return parse_key_value_output(result.stdout)


async def issue_get(
    *,
    number: int,
    repo: str | None = None,
) -> dict[str, Any]:
    args = [str(number)]
    if repo:
        args.append(repo)
    result = await async_run_script(
        "skills/gh-context/scripts/gh-issue-get.sh",
        *args,
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return parse_key_value_output(result.stdout)


async def issue_comments(
    *,
    number: int,
    repo: str | None = None,
) -> dict[str, Any]:
    args = [str(number)]
    if repo:
        args.append(repo)
    result = await async_run_script(
        "skills/gh-context/scripts/gh-issue-comments.sh",
        *args,
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw_output": result.stdout}


async def issue_create(
    *,
    title: str,
    body: str | None = None,
    labels: list[str] | None = None,
    repo: str | None = None,
) -> dict[str, Any]:
    args = [title]
    if body:
        args.extend(["--body", body])
    if labels:
        for label in labels:
            args.extend(["--label", label])
    if repo:
        args.extend(["--repo", repo])
    result = await async_run_script(
        "skills/gh-context/scripts/gh-issue-create.sh",
        *args,
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return parse_key_value_output(result.stdout)


async def pr_comments(
    *,
    action: str,
    pr_number: int | None = None,
    comment_id: int | str | None = None,
    comment_ids: list[str] | None = None,
    body: str | None = None,
    repo: str | None = None,
) -> dict[str, Any]:
    resolved_repo, err = await _resolve_repo(repo)
    if err:
        return err

    if action == "get":
        if comment_id is None:
            return {"error": "comment_id required for 'get' action"}
        result = await _gh_api(f"repos/{resolved_repo}/pulls/comments/{comment_id}")

    elif action == "list":
        if pr_number is None:
            return {"error": "pr_number required for 'list' action"}
        result = await _gh_api(
            f"repos/{resolved_repo}/pulls/{pr_number}/comments?per_page=100",
        )

    elif action == "reply":
        if pr_number is None or comment_id is None or body is None:
            return {"error": "pr_number, comment_id, and body required for 'reply'"}
        result = await _gh_api(
            f"repos/{resolved_repo}/pulls/{pr_number}/comments",
            method="POST",
            fields={"body": body, "in_reply_to": comment_id},
        )

    elif action == "resolve":
        ids_to_resolve: list[str] = []
        if comment_ids:
            ids_to_resolve = comment_ids
        elif comment_id is not None:
            ids_to_resolve = [str(comment_id)]
        else:
            return {"error": "comment_id or comment_ids required for 'resolve' action"}

        node_fragments = " ".join(
            f"n{i}: node(id: {json.dumps(cid)}) "
            f"{{ ... on PullRequestReviewComment "
            f"{{ pullRequestReviewThread {{ id }} }} }}"
            for i, cid in enumerate(ids_to_resolve)
        )
        query_result = await _gh_api(
            "graphql",
            fields={"query": f"{{ {node_fragments} }}"},
        )
        if query_result.returncode != 0:
            return {"error": query_result.stderr.strip()}

        query_data = json.loads(query_result.stdout)
        thread_ids: list[str] = []
        errors: list[str] = []
        for i, cid in enumerate(ids_to_resolve):
            node = query_data.get("data", {}).get(f"n{i}")
            thread = node.get("pullRequestReviewThread") if node else None
            if thread and thread["id"].startswith("PRRT_"):
                thread_ids.append(thread["id"])
            else:
                errors.append(
                    f"Could not find thread for comment {cid}. "
                    "The resolve action requires a GraphQL node_id, not a REST "
                    "integer ID. Use the node_id field from a comment response."
                )

        if not thread_ids:
            return {"error": "; ".join(errors)}

        resolve_fragments = " ".join(
            f"r{i}: resolveReviewThread(input: {{threadId: {json.dumps(tid)}}}) "
            f"{{ thread {{ id isResolved }} }}"
            for i, tid in enumerate(thread_ids)
        )
        result = await _gh_api(
            "graphql",
            fields={"query": f"mutation {{ {resolve_fragments} }}"},
        )

        if result.returncode != 0:
            return {"error": result.stderr.strip()}

        response: dict[str, Any] = json.loads(result.stdout)
        if errors:
            response["warnings"] = errors
        return response

    else:
        return {"error": f"Unknown action: {action}. Supported: list, get, reply, resolve"}

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw_output": result.stdout}


async def pr_comment_reply(
    *,
    pr_number: int,
    comment_id: int,
    body: str,
    repo: str | None = None,
) -> dict[str, Any]:
    resolved_repo, err = await _resolve_repo(repo)
    if err:
        return err

    result = await _gh_api(
        f"repos/{resolved_repo}/pulls/{pr_number}/comments",
        method="POST",
        fields={"body": body, "in_reply_to": comment_id},
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw_output": result.stdout}


async def request_review(
    *,
    pr_number: int,
    reviewers: list[str],
    team: bool | None = None,
    repo: str | None = None,
) -> dict[str, Any]:
    resolved_repo, err = await _resolve_repo(repo)
    if err:
        return err

    fields: dict[str, str | list[str]] = {}
    if team:
        fields["team_reviewers"] = [r.split("/")[-1] for r in reviewers]
    else:
        fields["reviewers"] = reviewers

    result = await _gh_api(
        f"repos/{resolved_repo}/pulls/{pr_number}/requested_reviewers",
        method="POST",
        fields=fields,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw_output": result.stdout}


async def detect_base_branch(
    *,
    base: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    args: list[str] = []
    if base:
        args.extend(["--base", base])
    if force:
        args.append("--force")

    result = await async_run_script(
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


async def verify_pr_state(*, force: bool = False) -> dict[str, Any]:
    args: list[str] = []
    if force:
        args.append("--force")

    result = await async_run_script(
        "skills/gh-pr-create/scripts/verify-state.sh",
        *args,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return parse_key_value_output(result.stdout)


async def pre_pr_checks(*, base_branch: str | None = None) -> dict[str, Any]:
    args: list[str] = []
    if base_branch:
        args.append(base_branch)

    result = await async_run_script(
        "skills/gh-pr-create/scripts/pre-pr-checks.sh",
        *args,
    )

    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        **({"error": result.stderr.strip()} if result.returncode != 0 else {}),
    }


async def create_pr(
    *,
    title: str,
    job_story: str,
    issue_id: str,
    fixes_url: str | None = None,
    base_branch: str | None = None,
) -> dict[str, Any]:
    args = [title, job_story, issue_id]
    args.append(fixes_url or "")
    args.append(base_branch or "")

    result = await async_run_script(
        "skills/gh-pr-create/scripts/create-pr.sh",
        *args,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    lines = result.stdout.strip().split("\n")
    pr_number = lines[-1]
    url = next((line for line in lines if line.startswith("http")), f"PR #{pr_number}")
    return {"pr_number": int(pr_number), "url": url}


async def generate_commit_list(
    *,
    pr_number: int,
    base_branch: str | None = None,
) -> dict[str, Any]:
    args = [str(pr_number)]
    if base_branch:
        args.append(base_branch)

    result = await async_run_script(
        "skills/gh-pr-create/scripts/generate-commit-list.sh",
        *args,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return {"commit_list": result.stdout.strip()}


async def post_summary_comment(
    *,
    issue_id: str,
    summary_text: str,
) -> dict[str, Any]:
    result = await async_run_script(
        "skills/gh-pr-create/scripts/post-summary-comment.sh",
        issue_id,
        summary_text,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return {"success": True, "output": result.stdout.strip()}


async def pr_notify(
    *,
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
) -> dict[str, Any]:
    plugin_root = Path(__file__).parents[3]
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

    proc = await async_run(args=args, timeout=60)

    if proc.returncode != 0:
        return {"error": proc.stderr.strip()}

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"success": True, "output": proc.stdout.strip()}
