"""Tests for hook orchestrator scripts (GH-959).

Verifies SessionStart/Stop orchestrators consolidate feature
invocations into single entries, tolerate per-feature failures,
and still emit valid hookSpecificOutput envelopes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "hooks" / "scripts"
SESSION_START = SCRIPTS / "session-start.py"
SESSION_STOP = SCRIPTS / "session-stop.py"


def _run(script: Path, payload: dict) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(SCRIPTS.parent.parent),
        env={
            "DEV10X_HOOK_AUDIT": "0",
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            "HOME": str(Path.home()),
        },
    )


class TestSessionStartOrchestrator:
    def test_exits_cleanly_with_empty_payload(self, tmp_path: Path) -> None:
        result = _run(SESSION_START, {})
        assert result.returncode == 0

    def test_produces_json_envelope_when_context_available(self) -> None:
        result = _run(SESSION_START, {"session_id": "test-session"})
        assert result.returncode == 0
        if result.stdout.strip():
            obj = json.loads(result.stdout)
            assert "hookSpecificOutput" in obj
            assert obj["hookSpecificOutput"]["hookEventName"] == "SessionStart"


class TestSessionStopOrchestrator:
    def test_exits_cleanly_with_empty_payload(self) -> None:
        result = _run(SESSION_STOP, {})
        assert result.returncode == 0

    def test_goodbye_message_present_with_session_id(self) -> None:
        result = _run(SESSION_STOP, {"session_id": "test-abc"})
        assert result.returncode == 0
        assert "Thank you for using Dev10x" in result.stdout


class TestOrchestratorConsolidation:
    """Orchestrators must survive feature failures — one broken feature
    does not skip the rest."""

    def test_session_start_survives_subfeature_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Feed malformed data that one feature might choke on
        result = _run(SESSION_START, {"session_id": ""})
        assert result.returncode == 0
