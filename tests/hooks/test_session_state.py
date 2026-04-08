"""Tests for session-stop-persist.sh and session-start-reload.py hooks."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STOP_HOOK = _REPO_ROOT / "hooks" / "scripts" / "session-stop-persist.sh"
START_HOOK = _REPO_ROOT / "hooks" / "scripts" / "session-start-reload.py"


def _run_hook(
    *,
    hook: Path,
    payload: dict | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    import os

    run_env = {**os.environ, **(env or {})}
    stdin_data = json.dumps(payload or {})
    cmd = ["bash", str(hook)] if hook.suffix == ".sh" else [str(hook)]
    return subprocess.run(
        cmd,
        input=stdin_data,
        capture_output=True,
        text=True,
        timeout=10,
        env=run_env,
    )


class TestSessionStopPersist:
    def test_exits_successfully_with_session_id(self) -> None:
        result = _run_hook(
            hook=STOP_HOOK,
            payload={"session_id": "test-session-123"},
        )
        assert result.returncode == 0

    def test_exits_successfully_without_session_id(self) -> None:
        result = _run_hook(hook=STOP_HOOK, payload={})
        assert result.returncode == 0

    def test_creates_state_file(self, tmp_path: Path) -> None:
        state_dir = tmp_path / ".claude" / "projects" / "_session_state"
        result = _run_hook(
            hook=STOP_HOOK,
            payload={"session_id": "test-session-456"},
            env={"HOME": str(tmp_path)},
        )
        assert result.returncode == 0
        state_files = list(state_dir.glob("*.json"))
        assert len(state_files) == 1
        state = json.loads(state_files[0].read_text())
        assert state["session_id"] == "test-session-456"
        assert "branch" in state
        assert "timestamp" in state

    def test_state_file_contains_git_info(self, tmp_path: Path) -> None:
        state_dir = tmp_path / ".claude" / "projects" / "_session_state"
        _run_hook(
            hook=STOP_HOOK,
            payload={"session_id": "test-session-789"},
            env={"HOME": str(tmp_path)},
        )
        state_files = list(state_dir.glob("*.json"))
        state = json.loads(state_files[0].read_text())
        assert isinstance(state["modified_files"], list)
        assert isinstance(state["staged_files"], list)
        assert isinstance(state["recent_commits"], list)


class TestSessionStartReload:
    def test_exits_successfully_without_state(self) -> None:
        result = _run_hook(hook=START_HOOK)
        assert result.returncode == 0

    def test_outputs_nothing_without_state(self, tmp_path: Path) -> None:
        result = _run_hook(
            hook=START_HOOK,
            env={"HOME": str(tmp_path)},
        )
        assert result.stdout == ""

    def test_outputs_context_with_state(self, tmp_path: Path) -> None:
        _run_hook(
            hook=STOP_HOOK,
            payload={"session_id": "reload-test-session"},
            env={"HOME": str(tmp_path)},
        )
        result = _run_hook(
            hook=START_HOOK,
            env={"HOME": str(tmp_path)},
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "hookSpecificOutput" in output
        context = output["hookSpecificOutput"]["additionalContext"]
        assert "Prior session state detected" in context
        assert "reload-test-session" in context

    def test_cleans_up_state_after_reload(self, tmp_path: Path) -> None:
        _run_hook(
            hook=STOP_HOOK,
            payload={"session_id": "cleanup-test"},
            env={"HOME": str(tmp_path)},
        )
        state_dir = tmp_path / ".claude" / "projects" / "_session_state"
        assert len(list(state_dir.glob("*.json"))) == 1
        _run_hook(
            hook=START_HOOK,
            env={"HOME": str(tmp_path)},
        )
        assert len(list(state_dir.glob("*.json"))) == 0
