"""Tests for db_server SQL validation."""

from __future__ import annotations

import pytest
from sql_validation import is_read_only_sql


class TestIsReadOnlySql:
    @pytest.mark.parametrize(
        "sql",
        [
            "SELECT 1",
            "SELECT count(*) FROM users",
            "select * from orders where id = 5",
            "  SELECT id FROM t",
        ],
    )
    def test_allows_plain_select(self, sql: str) -> None:
        assert is_read_only_sql(sql=sql) is True

    @pytest.mark.parametrize(
        "sql",
        [
            "WITH cte AS (SELECT 1) SELECT * FROM cte",
            "WITH orders AS (SELECT id FROM orders) SELECT count(*) FROM orders",
            (
                "WITH active AS (SELECT * FROM users WHERE active = true), "
                "counts AS (SELECT department, count(*) FROM active GROUP BY department) "
                "SELECT * FROM counts"
            ),
            "with recursive tree as (select id from nodes) select * from tree",
        ],
    )
    def test_allows_read_only_cte(self, sql: str) -> None:
        assert is_read_only_sql(sql=sql) is True

    @pytest.mark.parametrize(
        "sql",
        [
            "EXPLAIN SELECT * FROM users",
            "EXPLAIN ANALYZE SELECT 1",
        ],
    )
    def test_allows_explain(self, sql: str) -> None:
        assert is_read_only_sql(sql=sql) is True

    @pytest.mark.parametrize(
        "sql",
        [
            "SHOW search_path",
            "SHOW server_version",
        ],
    )
    def test_allows_show(self, sql: str) -> None:
        assert is_read_only_sql(sql=sql) is True

    @pytest.mark.parametrize(
        "sql",
        [
            "-- comment\nSELECT 1",
            "-- header\n-- another comment\nWITH cte AS (SELECT 1) SELECT * FROM cte",
        ],
    )
    def test_allows_sql_with_leading_comments(self, sql: str) -> None:
        assert is_read_only_sql(sql=sql) is True

    @pytest.mark.parametrize(
        "keyword",
        ["INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE"],
    )
    def test_blocks_write_keywords(self, keyword: str) -> None:
        assert is_read_only_sql(sql=f"{keyword} INTO users VALUES (1)") is False

    @pytest.mark.parametrize(
        "keyword",
        ["INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE"],
    )
    def test_blocks_write_keywords_inside_cte(self, keyword: str) -> None:
        sql = f"WITH cte AS ({keyword} INTO users VALUES (1) RETURNING id) SELECT * FROM cte"
        assert is_read_only_sql(sql=sql) is False

    @pytest.mark.parametrize(
        "keyword",
        [
            "GRANT",
            "REVOKE",
            "VACUUM",
            "REINDEX",
            "CLUSTER",
            "COPY",
            "LOCK",
            "DISCARD",
            "RESET",
            "REASSIGN",
        ],
    )
    def test_blocks_admin_keywords(self, keyword: str) -> None:
        assert is_read_only_sql(sql=f"{keyword} something") is False

    def test_blocks_refresh_materialized(self) -> None:
        assert is_read_only_sql(sql="REFRESH MATERIALIZED VIEW my_view") is False

    def test_blocks_unknown_prefix(self) -> None:
        assert is_read_only_sql(sql="CALL my_procedure()") is False

    def test_blocks_empty_string(self) -> None:
        assert is_read_only_sql(sql="") is False

    def test_blocks_comment_only(self) -> None:
        assert is_read_only_sql(sql="-- just a comment") is False
