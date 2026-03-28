#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""PostToolUse hook: persist task state to a YAML plan file.

Triggered on TaskCreate and TaskUpdate. Maintains a per-project
plan file that survives context compaction and session restarts.

Plan file location:
    <git-toplevel>/.claude/session/plan.yaml

CLI modes:
    (stdin)          — PostToolUse hook mode (default)
    --json-summary   — Read plan YAML, output JSON summary (for bash hooks)
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import yaml


def get_toplevel() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_plan_path(toplevel: str) -> Path:
    return Path(toplevel) / ".claude" / "session" / "plan.yaml"


def read_plan(plan_path: Path) -> dict:
    if plan_path.exists():
        try:
            with open(plan_path) as f:
                return yaml.safe_load(f) or {}
        except (yaml.YAMLError, OSError):
            return {}
    return {}


def write_plan_atomic(plan_path: Path, plan_data: dict) -> None:
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(plan_path.parent),
        prefix=".plan-",
        suffix=".yaml.tmp",
    )
    try:
        with os.fdopen(fd, "w") as f:
            yaml.dump(
                plan_data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )
        os.rename(tmp_path, str(plan_path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def extract_task_id(tool_result: str) -> str | None:
    match = re.search(r"Task #(\d+)", tool_result)
    return match.group(1) if match else None


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def get_branch() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def ensure_plan_metadata(plan: dict) -> None:
    if "plan" not in plan:
        plan["plan"] = {
            "created_at": now_iso(),
            "branch": get_branch(),
            "status": "in_progress",
        }
    plan["plan"]["last_synced"] = now_iso()


def handle_task_create(
    tool_input: dict,
    tool_result: str,
    plan: dict,
) -> bool:
    task_id = extract_task_id(tool_result)
    if not task_id:
        return False

    task_entry: dict = {
        "id": task_id,
        "subject": tool_input.get("subject", ""),
        "status": "pending",
        "created_at": now_iso(),
    }
    description = tool_input.get("description")
    if description:
        task_entry["description"] = description
    metadata = tool_input.get("metadata")
    if metadata:
        task_entry["metadata"] = metadata

    if "tasks" not in plan:
        plan["tasks"] = []

    existing_ids = {t.get("id") for t in plan["tasks"]}
    if task_id not in existing_ids:
        plan["tasks"].append(task_entry)
        return True
    return False


def handle_task_update(tool_input: dict, plan: dict) -> None:
    task_id = tool_input.get("taskId")
    if not task_id or "tasks" not in plan:
        return

    status = tool_input.get("status")
    if status == "deleted":
        plan["tasks"] = [t for t in plan["tasks"] if t.get("id") != task_id]
        return

    for task in plan["tasks"]:
        if task.get("id") != task_id:
            continue
        if status:
            task["status"] = status
            if status == "completed":
                task["completed_at"] = now_iso()
            elif status == "in_progress":
                task["started_at"] = now_iso()
        if "subject" in tool_input:
            task["subject"] = tool_input["subject"]
        if "description" in tool_input:
            task["description"] = tool_input["description"]
        if "metadata" in tool_input:
            existing_meta = task.get("metadata", {})
            for k, v in tool_input["metadata"].items():
                if v is None:
                    existing_meta.pop(k, None)
                else:
                    existing_meta[k] = v
            if existing_meta:
                task["metadata"] = existing_meta
        break


def cmd_json_summary() -> None:
    toplevel = get_toplevel()
    if not toplevel:
        json.dump({}, sys.stdout)
        sys.exit(0)

    plan_path = get_plan_path(toplevel=toplevel)
    plan = read_plan(plan_path=plan_path)
    if not plan.get("plan"):
        json.dump({}, sys.stdout)
        sys.exit(0)

    json.dump(plan, sys.stdout, indent=2)


def cmd_hook() -> None:
    payload_str = sys.stdin.read()
    if not payload_str.strip():
        sys.exit(0)

    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = payload.get("tool_input", {})
    tool_result = payload.get("tool_result", "")
    if isinstance(tool_result, dict):
        tool_result = tool_result.get("content", str(tool_result))

    tool_name = payload.get("tool_name", "")

    toplevel = get_toplevel()
    if not toplevel:
        sys.exit(0)

    plan_path = get_plan_path(toplevel=toplevel)
    plan = read_plan(plan_path=plan_path)
    is_new_plan = "plan" not in plan
    ensure_plan_metadata(plan)

    changed = False
    if tool_name == "TaskCreate":
        changed = handle_task_create(
            tool_input=tool_input,
            tool_result=tool_result,
            plan=plan,
        )
    elif tool_name == "TaskUpdate":
        handle_task_update(tool_input=tool_input, plan=plan)
        changed = True
    else:
        sys.exit(0)

    if is_new_plan and not changed:
        sys.exit(0)

    all_statuses = [t.get("status") for t in plan.get("tasks", [])]
    if all_statuses and all(s == "completed" for s in all_statuses):
        plan["plan"]["status"] = "completed"
        plan["plan"]["completed_at"] = now_iso()

    write_plan_atomic(plan_path=plan_path, plan_data=plan)


def main() -> None:
    if "--json-summary" in sys.argv:
        cmd_json_summary()
    else:
        cmd_hook()


if __name__ == "__main__":
    main()
