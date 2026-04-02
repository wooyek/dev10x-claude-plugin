#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Check CI status for a PR and return a structured JSON verdict.

Wraps `gh pr checks --json` and summarizes check states into a single
verdict that agents can rely on without parsing text tables. Also checks
the PR's mergeable status so merge conflicts block the verdict.

Usage:
    ci-check-status.py --pr 42 --repo owner/repo
    ci-check-status.py --pr 42 --repo owner/repo --required-only

Output (JSON):
    {
        "verdict": "pending",      # "green", "pending", "failing",
                                   # "conflicting", "empty"
        "mergeable": "MERGEABLE",  # "MERGEABLE", "CONFLICTING", "UNKNOWN"
        "total": 5,
        "pass": 3,
        "fail": 0,
        "pending": 2,
        "skipping": 0,
        "cancel": 0,
        "checks": [
            {"name": "build", "bucket": "pass"},
            {"name": "test", "bucket": "pending"},
            ...
        ]
    }

Verdict logic:
    - "conflicting" → PR has merge conflicts (regardless of CI status)
    - "empty"       → no checks found (GitHub hasn't registered suites yet)
    - "failing"     → at least one check failed
    - "pending"     → at least one check is pending (none failing)
    - "green"       → all non-skipping checks passed and no conflicts
"""

import argparse
import json
import subprocess
import sys


def fetch_mergeable(
    *,
    pr_number: int,
    repo: str,
) -> str:
    cmd = [
        "gh",
        "pr",
        "view",
        str(pr_number),
        "--repo",
        repo,
        "--json",
        "mergeable",
        "-q",
        ".mergeable",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return "UNKNOWN"
    return result.stdout.strip() or "UNKNOWN"


def fetch_checks(
    *,
    pr_number: int,
    repo: str,
    required_only: bool = False,
) -> list[dict]:
    cmd = [
        "gh",
        "pr",
        "checks",
        str(pr_number),
        "--repo",
        repo,
        "--json",
        "name,bucket,state",
    ]
    if required_only:
        cmd.append("--required")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            json.dumps({"error": f"gh pr checks failed: {result.stderr.strip()}"}),
            file=sys.stderr,
        )
        sys.exit(1)
    return json.loads(result.stdout)


def compute_verdict(
    *,
    checks: list[dict],
    mergeable: str = "UNKNOWN",
) -> dict:
    counts: dict[str, int] = {
        "pass": 0,
        "fail": 0,
        "pending": 0,
        "skipping": 0,
        "cancel": 0,
    }
    for check in checks:
        bucket = check.get("bucket", "pending")
        if bucket in counts:
            counts[bucket] += 1
        else:
            counts["pending"] += 1

    non_skipping = counts["pass"] + counts["fail"] + counts["pending"] + counts["cancel"]

    if mergeable == "CONFLICTING":
        verdict = "conflicting"
    elif not checks:
        verdict = "empty"
    elif counts["fail"] > 0:
        verdict = "failing"
    elif counts["pending"] > 0 or counts["cancel"] > 0:
        verdict = "pending"
    elif non_skipping == 0:
        verdict = "empty"
    else:
        verdict = "green"

    return {
        "verdict": verdict,
        "mergeable": mergeable,
        "total": len(checks),
        **counts,
        "checks": [
            {"name": c.get("name", "unknown"), "bucket": c.get("bucket", "pending")}
            for c in checks
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check CI status for a PR")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument(
        "--required-only",
        action="store_true",
        help="Only check required status checks",
    )
    args = parser.parse_args()

    checks = fetch_checks(
        pr_number=args.pr,
        repo=args.repo,
        required_only=args.required_only,
    )
    mergeable = fetch_mergeable(
        pr_number=args.pr,
        repo=args.repo,
    )
    result = compute_verdict(checks=checks, mergeable=mergeable)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
