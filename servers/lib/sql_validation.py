"""Read-only SQL validation for the db MCP server."""

from __future__ import annotations

import re

SAFE_PREFIX_RE = re.compile(
    r"^(SELECT|WITH|EXPLAIN|SHOW)\b",
    re.IGNORECASE,
)

BLOCKED_KEYWORD_RE = re.compile(
    r"\b("
    r"INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|"
    r"GRANT|REVOKE|VACUUM|REINDEX|CLUSTER|COPY|"
    r"DO\s*\$|BEGIN|COMMIT|ROLLBACK|SAVEPOINT|"
    r"SET\s+(?!search_path|statement_timeout|default_transaction_read_only)|"
    r"LOCK|DISCARD|RESET|"
    r"COMMENT\s+ON|SECURITY\s+LABEL|REASSIGN|"
    r"REFRESH\s+MATERIALIZED"
    r")\b",
    re.IGNORECASE,
)


def is_read_only_sql(sql: str) -> bool:
    """Check if SQL statement is read-only.

    Accepts SELECT, WITH (CTEs), EXPLAIN, and SHOW as safe prefixes.
    Blocks any statement containing write keywords even inside CTEs.
    """
    sql_clean = re.sub(r"^\s*(--.*)?", "", sql, flags=re.MULTILINE).strip()

    if not SAFE_PREFIX_RE.match(sql_clean):
        return False

    if BLOCKED_KEYWORD_RE.search(sql_clean):
        return False

    return True
