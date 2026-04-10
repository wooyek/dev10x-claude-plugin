from datetime import UTC, datetime, timedelta

import pytest

from dev10x.hooks.session import _format_plan_summary, _format_session_state


class TestFormatSessionState:
    @pytest.fixture()
    def state(self) -> dict:
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "branch": "janusz/GH-100/fix-bug",
            "worktree": "dev10x-ai-2",
            "session_id": "abc-123",
            "modified_files": ["src/app.py"],
            "staged_files": [],
            "recent_commits": ["abc1234 Fix the bug"],
        }

    def test_includes_branch(self, state: dict) -> None:
        result = _format_session_state(state=state)
        assert "janusz/GH-100/fix-bug" in result

    def test_includes_worktree(self, state: dict) -> None:
        result = _format_session_state(state=state)
        assert "dev10x-ai-2" in result

    def test_includes_session_id(self, state: dict) -> None:
        result = _format_session_state(state=state)
        assert "abc-123" in result

    def test_includes_modified_files(self, state: dict) -> None:
        result = _format_session_state(state=state)
        assert "src/app.py" in result

    def test_includes_resume_command(self, state: dict) -> None:
        result = _format_session_state(state=state)
        assert "claude --resume abc-123" in result

    def test_marks_stale_sessions(self) -> None:
        old_time = (datetime.now(UTC) - timedelta(hours=30)).isoformat()
        state = {"timestamp": old_time, "branch": "b", "session_id": "s"}
        result = _format_session_state(state=state)
        assert "STALE" in result

    def test_returns_empty_without_timestamp(self) -> None:
        result = _format_session_state(state={"branch": "b"})
        assert result == ""

    def test_omits_worktree_when_empty(self) -> None:
        state = {
            "timestamp": datetime.now(UTC).isoformat(),
            "branch": "main",
            "worktree": "",
            "session_id": "s",
        }
        result = _format_session_state(state=state)
        assert "Worktree" not in result


class TestFormatPlanSummary:
    @pytest.fixture()
    def plan(self) -> dict:
        return {
            "plan": {
                "status": "in_progress",
                "branch": "janusz/GH-50/feature",
                "last_synced": "2026-04-10T12:00:00Z",
                "context": {
                    "work_type": "feature",
                    "tickets": ["GH-50"],
                },
            },
            "tasks": [
                {"id": "1", "subject": "Set up workspace", "status": "completed"},
                {"id": "2", "subject": "Implement", "status": "in_progress"},
                {"id": "3", "subject": "Test", "status": "pending"},
            ],
        }

    def test_includes_task_counts(self, plan: dict) -> None:
        result = _format_plan_summary(plan=plan)
        assert "1/3 tasks completed" in result

    def test_includes_plan_branch(self, plan: dict) -> None:
        result = _format_plan_summary(plan=plan)
        assert "janusz/GH-50/feature" in result

    def test_includes_pending_tasks(self, plan: dict) -> None:
        result = _format_plan_summary(plan=plan)
        assert "Implement" in result
        assert "Test" in result

    def test_excludes_completed_from_remaining(self, plan: dict) -> None:
        result = _format_plan_summary(plan=plan)
        lines = [l for l in result.splitlines() if "Set up workspace" in l]
        assert not lines

    def test_includes_work_type(self, plan: dict) -> None:
        result = _format_plan_summary(plan=plan)
        assert "feature" in result

    def test_includes_tickets(self, plan: dict) -> None:
        result = _format_plan_summary(plan=plan)
        assert "GH-50" in result

    def test_shows_archive_hint_when_completed(self) -> None:
        plan = {
            "plan": {"status": "completed", "branch": "b", "last_synced": "t"},
            "tasks": [],
        }
        result = _format_plan_summary(plan=plan)
        assert "archived" in result.lower()

    def test_handles_empty_plan(self) -> None:
        result = _format_plan_summary(plan={})
        assert "0/0 tasks completed" in result
