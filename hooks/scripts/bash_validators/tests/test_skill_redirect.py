"""Tests for SkillRedirectValidator."""

from __future__ import annotations

import pytest

from bash_validators._types import HookInput
from bash_validators.skill_redirect import SkillRedirectValidator


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
