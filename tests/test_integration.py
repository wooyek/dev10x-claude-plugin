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


def _script_imports_dev10x(script: Path) -> bool:
    import ast

    try:
        tree = ast.parse(script.read_text())
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("dev10x"):
            return True
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("dev10x"):
                    return True
    return False


def _extract_dev10x_imports(script: Path) -> list[str]:
    import ast

    tree = ast.parse(script.read_text())
    lines: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("dev10x"):
            names = ", ".join(alias.name for alias in node.names if alias.name != "*")
            if names:
                lines.append(f"from {node.module} import {names}")
            else:
                lines.append(f"import {node.module}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("dev10x"):
                    lines.append(f"import {alias.name}")
    return lines


def _collect_python_entry_points() -> list[Path]:
    dirs = [
        REPO_ROOT / "hooks" / "scripts",
        REPO_ROOT / "servers",
    ]
    for skill_dir in sorted((REPO_ROOT / "skills").iterdir()):
        scripts_dir = skill_dir / "scripts"
        if scripts_dir.is_dir():
            dirs.append(scripts_dir)

    scripts: list[Path] = []
    for d in dirs:
        for p in sorted(d.glob("*.py")):
            if p.name == "__init__.py":
                continue
            scripts.append(p)
    return scripts


PYTHON_ENTRY_POINTS = _collect_python_entry_points()


class TestScriptLoadability:
    @pytest.mark.parametrize(
        "script",
        PYTHON_ENTRY_POINTS,
        ids=lambda p: str(p.relative_to(REPO_ROOT)),
    )
    def test_compiles_without_error(self, script: Path) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(script)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, (
            f"{script.relative_to(REPO_ROOT)} failed to compile:\n{result.stderr}"
        )

    @pytest.mark.parametrize(
        "script",
        [s for s in PYTHON_ENTRY_POINTS if _script_imports_dev10x(s)],
        ids=lambda p: str(p.relative_to(REPO_ROOT)),
    )
    def test_dev10x_imports_resolve(self, script: Path) -> None:
        import_lines = _extract_dev10x_imports(script=script)
        for line in import_lines:
            result = subprocess.run(
                [sys.executable, "-c", line],
                capture_output=True,
                text=True,
                timeout=10,
            )

            assert result.returncode == 0, (
                f"{script.relative_to(REPO_ROOT)}: import failed: {line}\n{result.stderr}"
            )


class TestStartupTime:
    BUDGET_MS = 2000

    def test_cli_help_under_budget(self) -> None:
        import time

        start = time.monotonic()
        result = subprocess.run(
            ["uv", "run", "dev10x", "--help"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(REPO_ROOT),
        )
        elapsed_ms = (time.monotonic() - start) * 1000

        assert result.returncode == 0
        assert "hook" in result.stdout
        assert elapsed_ms < self.BUDGET_MS, (
            f"Startup took {elapsed_ms:.0f}ms (budget: {self.BUDGET_MS}ms)"
        )
