"""Tests for block-sensitive-file-write.py hook."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / "scripts" / "block-sensitive-file-write.py"


def _run_hook(*, file_path: str) -> subprocess.CompletedProcess[str]:
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": file_path},
    }
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


class TestBlocksSensitiveFiles:
    @pytest.mark.parametrize(
        "file_path",
        [
            "/work/project/.env",
            "/work/project/secrets.env",
            "/work/project/credentials.json",
            "/work/project/.secret",
            "/work/project/config/.env.production",
            "/work/project/deploy/secrets.env.local",
        ],
    )
    def test_blocks_sensitive_file_paths(self, file_path: str) -> None:
        result = _run_hook(file_path=file_path)
        assert result.returncode == 2
        stderr = json.loads(result.stderr)
        assert stderr["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "sensitive" in stderr["systemMessage"].lower()


class TestAllowsSafeFiles:
    @pytest.mark.parametrize(
        "file_path",
        [
            "/work/project/src/main.py",
            "/work/project/README.md",
            "/work/project/config/database.yml",
            "/work/project/environment.py",
            "/work/project/config/settings.py",
            "/tmp/claude/gh-issues/001-setup.json",
            "/tmp/claude/gh-issues/001-setup.env.json",
        ],
    )
    def test_allows_non_sensitive_files(self, file_path: str) -> None:
        result = _run_hook(file_path=file_path)
        assert result.returncode == 0


class TestMalformedInput:
    def test_handles_empty_stdin(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            input="",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_handles_missing_file_path(self) -> None:
        payload = {"tool_name": "Edit", "tool_input": {}}
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
