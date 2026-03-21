"""Tests for skill-metrics.sh PostToolUse hook."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "scripts" / "skill-metrics.sh"


def _run_hook(
    *,
    payload: dict | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    run_env = {**os.environ, **(env or {})}
    stdin_data = json.dumps(payload or {})
    return subprocess.run(
        ["bash", str(HOOK)],
        input=stdin_data,
        capture_output=True,
        text=True,
        timeout=10,
        env=run_env,
    )


class TestSkillMetrics:
    def test_exits_successfully_with_valid_payload(self, tmp_path: Path) -> None:
        result = _run_hook(
            payload={
                "tool_input": {"skill": "Dev10x:git-commit"},
                "session_id": "metrics-test-1",
            },
            env={"HOME": str(tmp_path)},
        )
        assert result.returncode == 0

    def test_exits_silently_without_skill_name(self) -> None:
        result = _run_hook(payload={"tool_input": {}, "session_id": "s1"})
        assert result.returncode == 0

    def test_exits_silently_without_session_id(self) -> None:
        result = _run_hook(payload={"tool_input": {"skill": "test"}, "session_id": ""})
        assert result.returncode == 0

    def test_creates_metrics_file(self, tmp_path: Path) -> None:
        _run_hook(
            payload={
                "tool_input": {"skill": "Dev10x:git-commit"},
                "session_id": "metrics-test-2",
            },
            env={"HOME": str(tmp_path)},
        )
        metrics_dir = tmp_path / ".claude" / "projects" / "_metrics"
        jsonl_files = list(metrics_dir.glob("*.jsonl"))
        assert len(jsonl_files) == 1

    def test_metrics_entry_contains_skill_name(self, tmp_path: Path) -> None:
        _run_hook(
            payload={
                "tool_input": {"skill": "Dev10x:review"},
                "session_id": "metrics-test-3",
            },
            env={"HOME": str(tmp_path)},
        )
        metrics_dir = tmp_path / ".claude" / "projects" / "_metrics"
        jsonl_files = list(metrics_dir.glob("*.jsonl"))
        line = jsonl_files[0].read_text().strip()
        entry = json.loads(line)
        assert entry["skill"] == "Dev10x:review"
        assert entry["session"] == "metrics-test-3"
        assert "timestamp" in entry

    def test_appends_multiple_entries(self, tmp_path: Path) -> None:
        for i in range(3):
            _run_hook(
                payload={
                    "tool_input": {"skill": f"Dev10x:skill-{i}"},
                    "session_id": "metrics-test-4",
                },
                env={"HOME": str(tmp_path)},
            )
        metrics_dir = tmp_path / ".claude" / "projects" / "_metrics"
        jsonl_files = list(metrics_dir.glob("*.jsonl"))
        lines = jsonl_files[0].read_text().strip().split("\n")
        assert len(lines) == 3
