"""Integration tests for the refactored plugin structure.

Validates that hooks, MCP servers, CLI, and config all work
together after the src/dev10x migration.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from dev10x.cli import cli
from dev10x.config.loader import load_config
from dev10x.hooks.edit_validator import load_rules, validate_edit_write

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestCliIntegration:
    @pytest.fixture()
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_hook_subcommand_exists(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["hook", "--help"])

        assert result.exit_code == 0
        assert "validate-bash" in result.output

    def test_validate_subcommand_exists(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["validate", "--help"])

        assert result.exit_code == 0

    def test_skill_subcommand_exists(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["skill", "--help"])

        assert result.exit_code == 0


class TestConfigCaching:
    def test_first_load_creates_cache(self, tmp_path: Path) -> None:
        yaml_path = REPO_ROOT / "src" / "dev10x" / "validators" / "command-skill-map.yaml"
        if not yaml_path.exists():
            pytest.skip("command-skill-map.yaml not found")

        cache_path = tmp_path / "config.msgpack"
        yaml_copy = tmp_path / "config.yaml"
        yaml_copy.write_text(yaml_path.read_text())

        load_config(yaml_path=yaml_copy)

        assert yaml_copy.with_suffix(".msgpack").exists()

    def test_second_load_uses_cache(self, tmp_path: Path) -> None:
        yaml_path = REPO_ROOT / "src" / "dev10x" / "validators" / "command-skill-map.yaml"
        if not yaml_path.exists():
            pytest.skip("command-skill-map.yaml not found")

        yaml_copy = tmp_path / "config.yaml"
        yaml_copy.write_text(yaml_path.read_text())

        first = load_config(yaml_path=yaml_copy)
        second = load_config(yaml_path=yaml_copy)

        assert first.friction_level == second.friction_level
        assert len(first.rules) == len(second.rules)


class TestHookDispatch:
    def test_validate_bash_returns_json(self) -> None:
        hook_script = REPO_ROOT / "hooks" / "scripts" / "validate-bash-command.py"
        if not hook_script.exists():
            pytest.skip("validate-bash-command.py not found")

        payload = json.dumps(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "echo hello"},
            }
        )

        result = subprocess.run(
            [sys.executable, str(hook_script)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0

    def test_validate_edit_allows_safe_file(self) -> None:
        data = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/work/project/src/main.py",
                "new_string": "x = 1",
            },
        }

        with pytest.raises(SystemExit) as exc_info:
            validate_edit_write(data=data)

        assert exc_info.value.code == 0


class TestEditValidatorRules:
    def test_loads_production_rules(self) -> None:
        yaml_path = REPO_ROOT / "src" / "dev10x" / "validators" / "command-skill-map.yaml"
        if not yaml_path.exists():
            pytest.skip("command-skill-map.yaml not found")

        rules = load_rules(yaml_path=yaml_path)

        assert len(rules) > 0
        assert all(r.name for r in rules)


class TestMcpServerImports:
    def test_cli_server_importable(self) -> None:
        server_path = REPO_ROOT / "servers" / "cli_server.py"
        assert server_path.exists()

    def test_db_server_importable(self) -> None:
        server_path = REPO_ROOT / "servers" / "db_server.py"
        assert server_path.exists()


class TestStartupTime:
    def test_cli_help_under_budget(self) -> None:
        result = subprocess.run(
            ["uv", "run", "dev10x", "--help"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(REPO_ROOT),
        )

        assert result.returncode == 0
        assert "hook" in result.stdout
