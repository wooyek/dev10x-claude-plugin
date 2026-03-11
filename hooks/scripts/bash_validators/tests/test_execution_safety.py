"""Tests for ExecutionSafetyValidator."""

from __future__ import annotations

import pytest

from bash_validators._types import HookInput
from bash_validators.execution_safety import ExecutionSafetyValidator


def _make_input(*, command: str) -> HookInput:
    return HookInput(
        tool_name="Bash",
        command=command,
        raw={"tool_name": "Bash", "tool_input": {"command": command}},
    )


class TestShellWrites:
    @pytest.fixture()
    def validator(self) -> ExecutionSafetyValidator:
        return ExecutionSafetyValidator()

    @pytest.mark.parametrize(
        "command",
        [
            "cat > /tmp/file.txt",
            "cat << EOF > /tmp/file.txt",
            "echo hello > /tmp/file.txt",
            "echo hello >> /tmp/file.txt",
            "printf '%s' hello > /tmp/file.txt",
        ],
    )
    def test_blocks_shell_write_redirects(
        self, validator: ExecutionSafetyValidator, command: str
    ) -> None:
        inp = _make_input(command=command)
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Write/Edit tool" in result.message

    def test_allows_cat_without_redirect(
        self, validator: ExecutionSafetyValidator
    ) -> None:
        inp = _make_input(command="cat /tmp/file.txt")
        result = validator.validate(inp=inp)
        assert result is None


class TestPython3Inline:
    @pytest.fixture()
    def validator(self) -> ExecutionSafetyValidator:
        return ExecutionSafetyValidator()

    def test_blocks_python3_c(self, validator: ExecutionSafetyValidator) -> None:
        inp = _make_input(command='python3 -c "print(1)"')
        result = validator.validate(inp=inp)
        assert result is not None
        assert "python3" in result.message.lower()

    def test_allows_python3_module(self, validator: ExecutionSafetyValidator) -> None:
        inp = _make_input(command="python3 -m json.tool input.json")
        result = validator.validate(inp=inp)
        assert result is None

    def test_allows_approved_path(self, validator: ExecutionSafetyValidator) -> None:
        inp = _make_input(command="python3 ~/.claude/tools/script.py")
        result = validator.validate(inp=inp)
        assert result is None

    def test_blocks_untrusted_abs_path(
        self, validator: ExecutionSafetyValidator
    ) -> None:
        inp = _make_input(command="python3 /tmp/malicious.py")
        result = validator.validate(inp=inp)
        assert result is not None

    def test_allows_relative_path(self, validator: ExecutionSafetyValidator) -> None:
        inp = _make_input(command="python3 manage.py runserver")
        result = validator.validate(inp=inp)
        assert result is None
