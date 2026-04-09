from __future__ import annotations

import json
import subprocess
from unittest.mock import AsyncMock, patch

import pytest

gh = pytest.importorskip("dev10x.mcp.github", reason="dev10x not installed")


@pytest.fixture
def mock_resolve_repo():
    with patch.object(
        gh, "_resolve_repo", new_callable=AsyncMock, return_value=("owner/repo", None)
    ) as mock:
        yield mock


def _completed(
    *,
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


class TestPrCommentsResolveSingle:
    @pytest.fixture
    def query_response(self) -> str:
        return json.dumps({"data": {"n0": {"pullRequestReviewThread": {"id": "PRRT_thread123"}}}})

    @pytest.fixture
    def mutation_response(self) -> str:
        return json.dumps(
            {"data": {"r0": {"thread": {"id": "PRRT_thread123", "isResolved": True}}}}
        )

    @pytest.mark.asyncio
    @patch("dev10x.mcp.github._gh_api", new_callable=AsyncMock)
    async def test_resolves_single_comment(
        self,
        mock_api: AsyncMock,
        mock_resolve_repo: AsyncMock,
        query_response: str,
        mutation_response: str,
    ) -> None:
        mock_api.side_effect = [
            _completed(stdout=query_response),
            _completed(stdout=mutation_response),
        ]

        result = await gh.pr_comments(
            action="resolve",
            comment_id="PRRC_comment123",
        )

        assert result["data"]["r0"]["thread"]["isResolved"] is True
        assert mock_api.call_count == 2

    @pytest.mark.asyncio
    @patch("dev10x.mcp.github._gh_api", new_callable=AsyncMock)
    async def test_converts_int_comment_id_to_string(
        self,
        mock_api: AsyncMock,
        mock_resolve_repo: AsyncMock,
        query_response: str,
        mutation_response: str,
    ) -> None:
        mock_api.side_effect = [
            _completed(stdout=query_response),
            _completed(stdout=mutation_response),
        ]

        await gh.pr_comments(action="resolve", comment_id=12345)

        query_call = mock_api.call_args_list[0]
        query_str = query_call.kwargs["fields"]["query"]
        assert '"12345"' in query_str

    @pytest.mark.asyncio
    async def test_returns_error_when_no_comment_id(
        self,
        mock_resolve_repo: AsyncMock,
    ) -> None:
        result = await gh.pr_comments(action="resolve")

        assert "error" in result
        assert "comment_id or comment_ids required" in result["error"]


class TestPrCommentsResolveBatch:
    @pytest.fixture
    def comment_ids(self) -> list[str]:
        return ["PRRC_aaa", "PRRC_bbb", "PRRC_ccc"]

    @pytest.fixture
    def batch_query_response(self) -> str:
        return json.dumps(
            {
                "data": {
                    "n0": {"pullRequestReviewThread": {"id": "PRRT_t1"}},
                    "n1": {"pullRequestReviewThread": {"id": "PRRT_t2"}},
                    "n2": {"pullRequestReviewThread": {"id": "PRRT_t3"}},
                }
            }
        )

    @pytest.fixture
    def batch_mutation_response(self) -> str:
        return json.dumps(
            {
                "data": {
                    "r0": {"thread": {"id": "PRRT_t1", "isResolved": True}},
                    "r1": {"thread": {"id": "PRRT_t2", "isResolved": True}},
                    "r2": {"thread": {"id": "PRRT_t3", "isResolved": True}},
                }
            }
        )

    @pytest.mark.asyncio
    @patch("dev10x.mcp.github._gh_api", new_callable=AsyncMock)
    async def test_resolves_multiple_comments_in_two_calls(
        self,
        mock_api: AsyncMock,
        mock_resolve_repo: AsyncMock,
        comment_ids: list[str],
        batch_query_response: str,
        batch_mutation_response: str,
    ) -> None:
        mock_api.side_effect = [
            _completed(stdout=batch_query_response),
            _completed(stdout=batch_mutation_response),
        ]

        result = await gh.pr_comments(
            action="resolve",
            comment_ids=comment_ids,
        )

        assert mock_api.call_count == 2
        assert "data" in result
        assert "r0" in result["data"]
        assert "r1" in result["data"]
        assert "r2" in result["data"]

    @pytest.mark.asyncio
    @patch("dev10x.mcp.github._gh_api", new_callable=AsyncMock)
    async def test_batch_query_uses_aliased_nodes(
        self,
        mock_api: AsyncMock,
        mock_resolve_repo: AsyncMock,
        comment_ids: list[str],
        batch_query_response: str,
        batch_mutation_response: str,
    ) -> None:
        mock_api.side_effect = [
            _completed(stdout=batch_query_response),
            _completed(stdout=batch_mutation_response),
        ]

        await gh.pr_comments(action="resolve", comment_ids=comment_ids)

        query_call = mock_api.call_args_list[0]
        query_str = query_call.kwargs["fields"]["query"]
        assert "n0:" in query_str
        assert "n1:" in query_str
        assert "n2:" in query_str

    @pytest.mark.asyncio
    @patch("dev10x.mcp.github._gh_api", new_callable=AsyncMock)
    async def test_comment_ids_takes_precedence_over_comment_id(
        self,
        mock_api: AsyncMock,
        mock_resolve_repo: AsyncMock,
    ) -> None:
        mock_api.side_effect = [
            _completed(
                stdout=json.dumps({"data": {"n0": {"pullRequestReviewThread": {"id": "PRRT_t1"}}}})
            ),
            _completed(
                stdout=json.dumps(
                    {"data": {"r0": {"thread": {"id": "PRRT_t1", "isResolved": True}}}}
                )
            ),
        ]

        await gh.pr_comments(
            action="resolve",
            comment_id="PRRC_ignored",
            comment_ids=["PRRC_used"],
        )

        query_str = mock_api.call_args_list[0].kwargs["fields"]["query"]
        assert '"PRRC_used"' in query_str
        assert "PRRC_ignored" not in query_str


class TestPrCommentsResolveErrors:
    @pytest.mark.asyncio
    @patch("dev10x.mcp.github._gh_api", new_callable=AsyncMock)
    async def test_returns_error_when_query_fails(
        self,
        mock_api: AsyncMock,
        mock_resolve_repo: AsyncMock,
    ) -> None:
        mock_api.return_value = _completed(
            returncode=1,
            stderr="GraphQL error",
        )

        result = await gh.pr_comments(
            action="resolve",
            comment_id="PRRC_abc",
        )

        assert result["error"] == "GraphQL error"

    @pytest.mark.asyncio
    @patch("dev10x.mcp.github._gh_api", new_callable=AsyncMock)
    async def test_returns_error_when_thread_not_found(
        self,
        mock_api: AsyncMock,
        mock_resolve_repo: AsyncMock,
    ) -> None:
        mock_api.return_value = _completed(
            stdout=json.dumps({"data": {"n0": None}}),
        )

        result = await gh.pr_comments(
            action="resolve",
            comment_id="PRRC_bad",
        )

        assert "error" in result
        assert "Could not find thread" in result["error"]

    @pytest.mark.asyncio
    @patch("dev10x.mcp.github._gh_api", new_callable=AsyncMock)
    async def test_returns_error_when_thread_id_invalid(
        self,
        mock_api: AsyncMock,
        mock_resolve_repo: AsyncMock,
    ) -> None:
        mock_api.return_value = _completed(
            stdout=json.dumps(
                {"data": {"n0": {"pullRequestReviewThread": {"id": "INVALID_123"}}}}
            ),
        )

        result = await gh.pr_comments(
            action="resolve",
            comment_id="PRRC_bad",
        )

        assert "error" in result
        assert "Could not find thread" in result["error"]

    @pytest.mark.asyncio
    @patch("dev10x.mcp.github._gh_api", new_callable=AsyncMock)
    async def test_partial_failure_includes_warnings(
        self,
        mock_api: AsyncMock,
        mock_resolve_repo: AsyncMock,
    ) -> None:
        mock_api.side_effect = [
            _completed(
                stdout=json.dumps(
                    {
                        "data": {
                            "n0": {"pullRequestReviewThread": {"id": "PRRT_good"}},
                            "n1": None,
                        }
                    }
                )
            ),
            _completed(
                stdout=json.dumps(
                    {"data": {"r0": {"thread": {"id": "PRRT_good", "isResolved": True}}}}
                )
            ),
        ]

        result = await gh.pr_comments(
            action="resolve",
            comment_ids=["PRRC_good", "PRRC_bad"],
        )

        assert result["data"]["r0"]["thread"]["isResolved"] is True
        assert "warnings" in result
        assert any("PRRC_bad" in w for w in result["warnings"])

    @pytest.mark.asyncio
    @patch("dev10x.mcp.github._gh_api", new_callable=AsyncMock)
    async def test_mutation_error_returns_error(
        self,
        mock_api: AsyncMock,
        mock_resolve_repo: AsyncMock,
    ) -> None:
        mock_api.side_effect = [
            _completed(
                stdout=json.dumps({"data": {"n0": {"pullRequestReviewThread": {"id": "PRRT_t1"}}}})
            ),
            _completed(returncode=1, stderr="Mutation failed"),
        ]

        result = await gh.pr_comments(
            action="resolve",
            comment_id="PRRC_abc",
        )

        assert result["error"] == "Mutation failed"
