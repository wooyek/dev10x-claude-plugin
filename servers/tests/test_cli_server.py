"""Tests for servers/cli_server.py core infrastructure and tools.

This file covers the helper functions and a representative sample
of MCP tools. Full 100% coverage of all 21 tools is tracked in
GH-493 and will be completed incrementally.
"""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

# Import the server module — needs mcp available
cli_server = pytest.importorskip("cli_server", reason="mcp not installed")


class TestDetectRepo:
    @patch("cli_server.subprocess.run")
    def test_returns_repo_on_success(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="Brave-Labs/dev10x\n",
            stderr="",
        )

        result = cli_server._detect_repo()

        assert result == "Brave-Labs/dev10x"

    @patch("cli_server.subprocess.run")
    def test_returns_none_on_failure(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="not a git repo",
        )

        result = cli_server._detect_repo()

        assert result is None


class TestGhApi:
    @patch("cli_server.subprocess.run")
    def test_builds_get_command(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="{}",
            stderr="",
        )

        cli_server._gh_api(endpoint="/repos/owner/repo")

        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "gh"
        assert cmd[1] == "api"
        assert "/repos/owner/repo" in cmd
        assert "-X" not in cmd

    @patch("cli_server.subprocess.run")
    def test_adds_method_for_non_get(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="{}",
            stderr="",
        )

        cli_server._gh_api(
            endpoint="/repos/owner/repo/pulls",
            method="POST",
        )

        cmd = mock_run.call_args[0][0]
        assert "-X" in cmd
        post_idx = cmd.index("-X")
        assert cmd[post_idx + 1] == "POST"

    @patch("cli_server.subprocess.run")
    def test_adds_jq_filter(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="value",
            stderr="",
        )

        cli_server._gh_api(
            endpoint="/repos/owner/repo",
            jq=".name",
        )

        cmd = mock_run.call_args[0][0]
        assert "--jq" in cmd
        jq_idx = cmd.index("--jq")
        assert cmd[jq_idx + 1] == ".name"

    @patch("cli_server.subprocess.run")
    def test_handles_string_fields(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="{}",
            stderr="",
        )

        cli_server._gh_api(
            endpoint="/repos/owner/repo",
            method="POST",
            fields={"title": "My PR"},
        )

        cmd = mock_run.call_args[0][0]
        assert "-f" in cmd
        f_idx = cmd.index("-f")
        assert cmd[f_idx + 1] == "title=My PR"

    @patch("cli_server.subprocess.run")
    def test_handles_int_fields(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="{}",
            stderr="",
        )

        cli_server._gh_api(
            endpoint="/repos/owner/repo",
            method="POST",
            fields={"count": 42},
        )

        cmd = mock_run.call_args[0][0]
        assert "-F" in cmd
        f_idx = cmd.index("-F")
        assert cmd[f_idx + 1] == "count=42"

    @patch("cli_server.subprocess.run")
    def test_handles_list_fields(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="{}",
            stderr="",
        )

        cli_server._gh_api(
            endpoint="/repos/owner/repo",
            method="POST",
            fields={"reviewers": ["alice", "bob"]},
        )

        cmd = mock_run.call_args[0][0]
        assert "-f" in cmd
        f_indices = [i for i, c in enumerate(cmd) if c == "-f"]
        assert len(f_indices) == 2
        assert cmd[f_indices[0] + 1] == "reviewers[]=alice"
        assert cmd[f_indices[1] + 1] == "reviewers[]=bob"


class TestResolveRepo:
    def test_returns_provided_repo(self) -> None:
        result, error = cli_server._resolve_repo(repo="owner/repo")

        assert result == "owner/repo"
        assert error is None

    @patch("cli_server._detect_repo", return_value="detected/repo")
    def test_detects_repo_when_none_provided(
        self,
        _mock: MagicMock,
    ) -> None:
        result, error = cli_server._resolve_repo(repo=None)

        assert result == "detected/repo"
        assert error is None

    @patch("cli_server._detect_repo", return_value=None)
    def test_returns_error_when_detection_fails(
        self,
        _mock: MagicMock,
    ) -> None:
        result, error = cli_server._resolve_repo(repo=None)

        assert result is None
        assert error is not None
        assert "error" in error


class TestDetectTracker:
    @pytest.mark.asyncio
    @patch("cli_server.run_script")
    async def test_returns_parsed_output_on_success(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="TRACKER=github\nTICKET_ID=GH-15\nTICKET_NUMBER=15\nFIXES_URL=https://github.com/org/repo/issues/15",
            stderr="",
        )

        result = await cli_server.detect_tracker(ticket_id="GH-15")

        assert result["TRACKER"] == "github"
        assert result["TICKET_NUMBER"] == "15"

    @pytest.mark.asyncio
    @patch("cli_server.run_script")
    async def test_returns_error_on_failure(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="Unknown tracker",
        )

        result = await cli_server.detect_tracker(ticket_id="UNKNOWN-1")

        assert "error" in result


class TestMktmp:
    @pytest.mark.asyncio
    @patch("cli_server.run_script")
    async def test_creates_temp_file(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="/tmp/claude/git/commit-msg.abc123.txt",
            stderr="",
        )

        result = await cli_server.mktmp(
            namespace="git",
            prefix="commit-msg",
            ext=".txt",
        )

        assert result["path"] == "/tmp/claude/git/commit-msg.abc123.txt"
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0]
        assert call_args[0] == "bin/mktmp.sh"
        assert "git" in call_args
        assert "commit-msg" in call_args

    @pytest.mark.asyncio
    @patch("cli_server.run_script")
    async def test_creates_temp_directory(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="/tmp/claude/audit/session.abc123",
            stderr="",
        )

        result = await cli_server.mktmp(
            namespace="audit",
            prefix="session",
            directory=True,
        )

        assert result["path"] == "/tmp/claude/audit/session.abc123"
        call_args = mock_run.call_args[0]
        assert "-d" in call_args

    @pytest.mark.asyncio
    @patch("cli_server.run_script")
    async def test_returns_error_on_failure(
        self,
        mock_run: MagicMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="Permission denied",
        )

        result = await cli_server.mktmp(
            namespace="git",
            prefix="msg",
        )

        assert "error" in result
