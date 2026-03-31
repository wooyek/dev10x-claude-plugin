"""Tests for SkillRedirectValidator."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from bash_validators._types import HookInput
from bash_validators.skill_redirect import (
    SkillRedirectValidator,
    _load_config,
)


def _make_input(*, command: str) -> HookInput:
    return HookInput(
        tool_name="Bash",
        command=command,
        raw={"tool_name": "Bash", "tool_input": {"command": command}},
    )


@pytest.fixture()
def validator() -> SkillRedirectValidator:
    return SkillRedirectValidator()


class TestShouldRun:
    def test_true_for_git_commit(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command='git commit -m "some message"')
        assert validator.should_run(inp=inp) is True

    def test_true_for_gh_pr_create(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh pr create --title 'test'")
        assert validator.should_run(inp=inp) is True

    def test_true_for_git_push(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git push origin main")
        assert validator.should_run(inp=inp) is True

    def test_true_for_git_rebase(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git rebase -i HEAD~3")
        assert validator.should_run(inp=inp) is True

    def test_true_for_gh_pr_checks(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh pr checks --watch")
        assert validator.should_run(inp=inp) is True

    def test_false_for_unrelated_command(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git status")
        assert validator.should_run(inp=inp) is False

    def test_false_for_git_log(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git log --oneline -5")
        assert validator.should_run(inp=inp) is False


class TestGitCommitRedirect:
    def test_blocks_git_commit_with_m_flag(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command='git commit -m "Enable feature X"')
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:git-commit" in result.message

    def test_blocks_git_commit_with_m_single_quotes(
        self, validator: SkillRedirectValidator
    ) -> None:
        inp = _make_input(command="git commit -m 'Enable feature X'")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:git-commit" in result.message

    def test_allows_git_commit_f_with_skill_temp(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git commit -F /tmp/claude/git/commit-msg.W9DryMXsQ5Aw.txt")
        result = validator.validate(inp=inp)
        assert result is None

    def test_allows_git_commit_f_with_alternate_prefix(
        self, validator: SkillRedirectValidator
    ) -> None:
        inp = _make_input(command="git commit -F /tmp/claude/git/msg.RnUr0daBNpSj.txt")
        result = validator.validate(inp=inp)
        assert result is None

    def test_blocks_git_commit_f_with_arbitrary_path(
        self, validator: SkillRedirectValidator
    ) -> None:
        inp = _make_input(command="git commit -F /tmp/random/msg.txt")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:git-commit" in result.message

    def test_blocks_git_commit_f_with_non_git_namespace(
        self, validator: SkillRedirectValidator
    ) -> None:
        inp = _make_input(command="git commit -F /tmp/claude/commit/msg.knDXJdfzYnVI.txt")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "mcp__plugin_Dev10x_cli__mktmp" in result.message
        assert "wrong temp file path" in result.message

    def test_healing_msg_suggests_git_namespace(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git commit -F /tmp/claude/commit/msg.abc123.txt")
        result = validator.validate(inp=inp)
        assert result is not None
        assert 'namespace="git"' in result.message

    def test_blocks_git_commit_without_flags(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git commit")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:git-commit" in result.message

    def test_allows_git_commit_fixup(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git commit --fixup=abc1234")
        result = validator.validate(inp=inp)
        assert result is None

    def test_allows_git_commit_amend(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git commit --amend")
        result = validator.validate(inp=inp)
        assert result is None


class TestGhPrCreateRedirect:
    def test_blocks_gh_pr_create(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh pr create --title 'Fix bug' --body 'details'")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:gh-pr-create" in result.message

    def test_blocks_gh_pr_create_minimal(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh pr create")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:gh-pr-create" in result.message


class TestGitPushRedirect:
    def test_blocks_git_push(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git push origin feature-branch")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:git" in result.message

    def test_blocks_git_push_force(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git push --force-with-lease")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:git" in result.message

    def test_blocks_git_push_u(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git push -u origin feature-branch")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:git" in result.message


class TestGitRebaseRedirect:
    def test_blocks_git_rebase_i(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git rebase -i HEAD~3")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:git-groom" in result.message

    def test_blocks_git_rebase_interactive(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git rebase --interactive HEAD~5")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:git-groom" in result.message

    def test_allows_git_rebase_continue(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git rebase --continue")
        result = validator.validate(inp=inp)
        assert result is None

    def test_allows_git_rebase_onto(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git rebase origin/develop")
        result = validator.validate(inp=inp)
        assert result is None


class TestGhPrChecksWatchRedirect:
    def test_blocks_gh_pr_checks_watch(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh pr checks --watch")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:gh-pr-monitor" in result.message

    def test_blocks_gh_pr_checks_w(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh pr checks -w")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Dev10x:gh-pr-monitor" in result.message

    def test_allows_gh_pr_checks_without_watch(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh pr checks")
        result = validator.validate(inp=inp)
        assert result is None

    def test_allows_gh_pr_checks_with_pr_number(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh pr checks 42")
        result = validator.validate(inp=inp)
        assert result is None


class TestGhIssueViewRedirect:
    def test_blocks_gh_issue_view(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh issue view 539 --repo Brave-Labs/dev10x")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "mcp__plugin_Dev10x_cli__issue_get" in result.message

    def test_blocks_gh_issue_view_with_json(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh issue view 42 --json title,body,state")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "mcp__plugin_Dev10x_cli__issue_get" in result.message

    def test_blocks_gh_issue_view_minimal(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh issue view 10")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "mcp__plugin_Dev10x_cli__issue_get" in result.message

    def test_mcp_message_uses_tool_label(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh issue view 1")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "MCP tool" in result.message
        assert "Skill(" not in result.message

    def test_should_run_true_for_gh_issue_view(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh issue view 539")
        assert validator.should_run(inp=inp) is True


class TestGhIssueCreateRedirect:
    def test_blocks_gh_issue_create(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh issue create --title 'Fix bug' --body 'Details'")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "mcp__plugin_Dev10x_cli__issue_create" in result.message

    def test_blocks_gh_issue_create_minimal(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh issue create --title 'New feature'")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "mcp__plugin_Dev10x_cli__issue_create" in result.message

    def test_mcp_message_uses_tool_label(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh issue create --title test")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "MCP tool" in result.message
        assert "Skill(" not in result.message

    def test_should_run_true_for_gh_issue_create(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="gh issue create --title test")
        assert validator.should_run(inp=inp) is True


class TestMessageContent:
    def test_message_includes_skill_name(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git push origin main")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "Skill(Dev10x:git)" in result.message

    def test_message_includes_guardrails(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git push origin main")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "protected branch" in result.message

    def test_message_includes_blocked_indicator(self, validator: SkillRedirectValidator) -> None:
        inp = _make_input(command="git push origin main")
        result = validator.validate(inp=inp)
        assert result is not None
        assert "blocked" in result.message


class TestFrictionLevels:
    def _make_yaml(
        self,
        *,
        friction_level: str,
        fallback: str = "",
        mapping_type: str = "skill",
    ) -> str:
        fallback_line = f'fallback_instructions: "{fallback}"' if fallback else ""
        return textwrap.dedent(
            f"""\
            config:
              friction_level: {friction_level}
            mappings:
              - skill: Dev10x:test-skill
                type: {mapping_type}
                patterns:
                  - test cmd
                hook_block: true
                hook_except: []
                guardrails: test guardrail
                {fallback_line}
            """
        )

    def test_guided_mode_includes_fallback(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "map.yaml"
        yaml_file.write_text(
            self._make_yaml(
                friction_level="guided",
                fallback="Apply manual guardrail here.",
            )
        )
        config = _load_config(yaml_path=yaml_file)
        assert config.friction_level == "guided"

        validator = SkillRedirectValidator()
        inp = _make_input(command="test cmd foo")

        import bash_validators.skill_redirect as mod

        original = mod._CONFIG
        mod._CONFIG = config
        try:
            result = validator.validate(inp=inp)
        finally:
            mod._CONFIG = original

        assert result is not None
        assert "Apply manual guardrail here." in result.message

    def test_strict_mode_omits_fallback(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "map.yaml"
        yaml_file.write_text(
            self._make_yaml(
                friction_level="strict",
                fallback="Apply manual guardrail here.",
            )
        )
        config = _load_config(yaml_path=yaml_file)

        validator = SkillRedirectValidator()
        inp = _make_input(command="test cmd foo")

        import bash_validators.skill_redirect as mod

        original = mod._CONFIG
        mod._CONFIG = config
        try:
            result = validator.validate(inp=inp)
        finally:
            mod._CONFIG = original

        assert result is not None
        assert "Apply manual guardrail here." not in result.message

    def test_hook_block_false_entries_not_loaded(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "map.yaml"
        yaml_file.write_text(
            textwrap.dedent(
                """\
                config:
                  friction_level: guided
                mappings:
                  - skill: Dev10x:ignored
                    patterns:
                      - ignored cmd
                    hook_block: false
                    guardrails: ""
                """
            )
        )
        config = _load_config(yaml_path=yaml_file)
        assert config.mappings == []

    def test_mcp_type_guided_uses_mcp_template(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "map.yaml"
        yaml_file.write_text(
            self._make_yaml(
                friction_level="guided",
                fallback="Use gh issue view directly.",
                mapping_type="mcp",
            )
        )
        config = _load_config(yaml_path=yaml_file)

        validator = SkillRedirectValidator()
        inp = _make_input(command="test cmd foo")

        import bash_validators.skill_redirect as mod

        original = mod._CONFIG
        mod._CONFIG = config
        try:
            result = validator.validate(inp=inp)
        finally:
            mod._CONFIG = original

        assert result is not None
        assert "MCP tool" in result.message
        assert "Skill(" not in result.message

    def test_mcp_type_strict_uses_mcp_template(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "map.yaml"
        yaml_file.write_text(
            self._make_yaml(
                friction_level="strict",
                mapping_type="mcp",
            )
        )
        config = _load_config(yaml_path=yaml_file)

        validator = SkillRedirectValidator()
        inp = _make_input(command="test cmd foo")

        import bash_validators.skill_redirect as mod

        original = mod._CONFIG
        mod._CONFIG = config
        try:
            result = validator.validate(inp=inp)
        finally:
            mod._CONFIG = original

        assert result is not None
        assert "MCP tool" in result.message
        assert "Skill(" not in result.message

    def test_mcp_type_loaded_from_yaml(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "map.yaml"
        yaml_file.write_text(
            self._make_yaml(
                friction_level="guided",
                mapping_type="mcp",
            )
        )
        config = _load_config(yaml_path=yaml_file)
        assert config.mappings[0].type == "mcp"

    def test_skill_type_is_default(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "map.yaml"
        yaml_file.write_text(self._make_yaml(friction_level="guided"))
        config = _load_config(yaml_path=yaml_file)
        assert config.mappings[0].type == "skill"


class TestYamlSchema:
    def test_yaml_file_is_valid(self) -> None:
        data = yaml.safe_load(_YAML_PATH.read_text())  # type: ignore[name-defined]  # noqa: F821
        assert "config" in data
        assert "mappings" in data
        assert data["config"]["friction_level"] in {"strict", "guided", "adaptive"}

    def test_all_hook_block_entries_have_guardrails(self) -> None:
        data = yaml.safe_load(_YAML_PATH.read_text())  # type: ignore[name-defined]  # noqa: F821
        for entry in data["mappings"]:
            if entry.get("hook_block"):
                assert "guardrails" in entry, f"{entry['skill']} missing guardrails"
                assert entry["guardrails"], f"{entry['skill']} has empty guardrails"

    def test_type_field_is_valid_when_present(self) -> None:
        data = yaml.safe_load(_YAML_PATH.read_text())  # type: ignore[name-defined]  # noqa: F821
        for entry in data["mappings"]:
            entry_type = entry.get("type", "skill")
            assert entry_type in {"skill", "mcp"}, (
                f"{entry['skill']} has invalid type: {entry_type}"
            )


# Make _YAML_PATH accessible for tests above
from bash_validators.skill_redirect import _YAML_PATH  # noqa: E402
