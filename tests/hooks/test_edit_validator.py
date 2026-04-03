"""Tests for dev10x.hooks.edit_validator — Edit/Write tool validation."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from dev10x.hooks.edit_validator import (
    EditRule,
    _basename,
    format_message,
    load_rules,
    matches_content,
    matches_file,
)


@pytest.fixture()
def rule_with_pattern() -> EditRule:
    return EditRule(
        name="block-env",
        file_pattern=re.compile(r"\.env$"),
        file_names=frozenset(),
        file_prefixes=(),
        file_substrings=(),
        content_pattern=None,
        message="BLOCKED: {file_path}",
    )


@pytest.fixture()
def rule_with_names() -> EditRule:
    return EditRule(
        name="block-secrets",
        file_pattern=None,
        file_names=frozenset({"credentials.json", "secrets.yaml"}),
        file_prefixes=(),
        file_substrings=(),
        content_pattern=None,
        message="BLOCKED: sensitive file",
    )


@pytest.fixture()
def rule_with_prefixes() -> EditRule:
    return EditRule(
        name="block-dot-env",
        file_pattern=None,
        file_names=frozenset(),
        file_prefixes=(".env",),
        file_substrings=(),
        content_pattern=None,
        message="BLOCKED: env file",
    )


@pytest.fixture()
def rule_with_substrings() -> EditRule:
    return EditRule(
        name="block-secret-dirs",
        file_pattern=None,
        file_names=frozenset(),
        file_prefixes=(),
        file_substrings=("/secrets/",),
        content_pattern=None,
        message="BLOCKED: secrets directory",
    )


@pytest.fixture()
def rule_with_content_pattern() -> EditRule:
    return EditRule(
        name="block-eval",
        file_pattern=re.compile(r"SKILL\.md$"),
        file_names=frozenset(),
        file_prefixes=(),
        file_substrings=(),
        content_pattern=re.compile(r"\beval\b"),
        message="BLOCKED: eval in skill",
    )


class TestBasename:
    def test_extracts_filename_from_path(self) -> None:
        assert _basename(path="/work/project/src/main.py") == "main.py"

    def test_returns_input_when_no_slash(self) -> None:
        assert _basename(path="main.py") == "main.py"


class TestMatchesFile:
    def test_matches_file_pattern(
        self,
        rule_with_pattern: EditRule,
    ) -> None:
        assert matches_file(rule=rule_with_pattern, file_path="/work/.env") is True

    def test_rejects_non_matching_pattern(
        self,
        rule_with_pattern: EditRule,
    ) -> None:
        assert matches_file(rule=rule_with_pattern, file_path="/work/main.py") is False

    def test_matches_file_names(
        self,
        rule_with_names: EditRule,
    ) -> None:
        assert matches_file(rule=rule_with_names, file_path="/work/credentials.json") is True

    def test_rejects_non_matching_names(
        self,
        rule_with_names: EditRule,
    ) -> None:
        assert matches_file(rule=rule_with_names, file_path="/work/config.json") is False

    def test_matches_file_prefixes(
        self,
        rule_with_prefixes: EditRule,
    ) -> None:
        assert matches_file(rule=rule_with_prefixes, file_path="/work/.env.production") is True

    def test_matches_file_substrings(
        self,
        rule_with_substrings: EditRule,
    ) -> None:
        assert (
            matches_file(
                rule=rule_with_substrings,
                file_path="/work/secrets/api.key",
            )
            is True
        )


class TestMatchesContent:
    def test_matches_when_no_content_pattern(
        self,
        rule_with_pattern: EditRule,
    ) -> None:
        assert matches_content(rule=rule_with_pattern, content="anything") is True

    def test_matches_content_pattern(
        self,
        rule_with_content_pattern: EditRule,
    ) -> None:
        assert matches_content(rule=rule_with_content_pattern, content="eval(code)") is True

    def test_rejects_non_matching_content(
        self,
        rule_with_content_pattern: EditRule,
    ) -> None:
        assert matches_content(rule=rule_with_content_pattern, content="safe code") is False


class TestFormatMessage:
    def test_formats_file_path(self, rule_with_pattern: EditRule) -> None:
        result = format_message(rule=rule_with_pattern, file_path="/work/.env")

        assert result == "BLOCKED: /work/.env"

    def test_appends_compensation_descriptions(self) -> None:
        rule = EditRule(
            name="test",
            file_pattern=None,
            file_names=frozenset(),
            file_prefixes=(),
            file_substrings=(),
            content_pattern=None,
            message="BLOCKED",
            compensations=[{"description": "Use the Write tool instead"}],
        )

        result = format_message(rule=rule, file_path="/work/file.py")

        assert "Use the Write tool instead" in result


class TestLoadRules:
    def test_loads_edit_write_rules(self, tmp_path: Path) -> None:
        yaml_content = {
            "rules": [
                {
                    "name": "block-env",
                    "matcher": "Edit|Write",
                    "hook_block": True,
                    "file_names": [".env"],
                    "reason": "Sensitive file",
                },
                {
                    "name": "bash-rule",
                    "matcher": "Bash",
                    "hook_block": True,
                    "patterns": ["^git push"],
                },
            ]
        }
        yaml_path = tmp_path / "rules.yaml"
        yaml_path.write_text(yaml.dump(yaml_content))

        rules = load_rules(yaml_path=yaml_path)

        assert len(rules) == 1
        assert rules[0].name == "block-env"

    def test_skips_non_blocking_rules(self, tmp_path: Path) -> None:
        yaml_content = {
            "rules": [
                {
                    "name": "advisory",
                    "matcher": "Edit|Write",
                    "hook_block": False,
                    "file_names": [".env"],
                },
            ]
        }
        yaml_path = tmp_path / "rules.yaml"
        yaml_path.write_text(yaml.dump(yaml_content))

        rules = load_rules(yaml_path=yaml_path)

        assert len(rules) == 0
