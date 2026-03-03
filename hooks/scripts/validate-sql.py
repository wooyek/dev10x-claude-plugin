#!/usr/bin/env python3
"""PreToolUse hook: validate SQL in db.sh / psql commands.

Reads Claude Code hook JSON from stdin, checks if the Bash command
is a db.sh or psql call, and validates that the SQL is read-only.

Exit codes:
  0 — allow (not a db command, or SQL is safe)
  2 — block (SQL contains write operations)
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys

POSTGRES_CONN_RE = re.compile(r"postgres://[^'\"\s]+:[^@'\"\s]+@[a-zA-Z0-9._-]+")

BLOCKED_KEYWORDS = re.compile(
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

SAFE_PREFIXES = re.compile(
    r"^\s*(SELECT|WITH|EXPLAIN|SHOW|\\d|\\dt|\\l)\b",
    re.IGNORECASE,
)

_PLUGIN_ROOT = os.environ.get(
    "CLAUDE_PLUGIN_ROOT",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)
DB_SH_PATH = os.path.join(_PLUGIN_ROOT, "skills", "db-psql", "scripts", "db.sh")


def _is_psql_binary(token: str) -> bool:
    return token == "psql" or token.endswith("/psql")


def _is_db_sh(token: str) -> bool:
    return token.endswith("db.sh") or token.endswith("/db.sh")


def _split_pipe_segments(command: str) -> list[str]:
    """Split a command into pipe-delimited segments, respecting shell quoting.

    Literal ``|`` characters inside quoted strings are preserved within
    their segment rather than treated as pipe delimiters.  The original
    quoting is retained in each segment so downstream ``shlex.split``
    calls can properly reconstruct arguments.
    """
    segments: list[str] = []
    current_start = 0
    in_single = False
    in_double = False
    escape = False
    for i, ch in enumerate(command):
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            continue
        if ch == "|" and not in_single and not in_double:
            segments.append(command[current_start:i])
            current_start = i + 1
    segments.append(command[current_start:])
    return segments


def extract_sql_from_command(command: str) -> str | None:
    """Extract SQL string from a db.sh command line.

    Only inspects the first command in a pipe chain to avoid false
    positives from commands that merely mention db.sh in arguments.
    Uses shell-aware splitting so literal ``|`` inside quoted SQL
    (e.g. bitwise OR, string concatenation) is not mistaken for a pipe.

    Direct psql calls are blocked earlier in ``main()`` and never reach
    this function.
    """
    first_cmd = _split_pipe_segments(command)[0].strip()

    try:
        parts = shlex.split(first_cmd)
    except ValueError:
        return None

    if not parts:
        return None

    if not _is_db_sh(parts[0]):
        return None

    if "--list" in parts or "-l" in parts:
        return None
    if "-f" in parts or "--file" in parts:
        flag_idx = next(
            (i for i, p in enumerate(parts) if p in ("-f", "--file")),
            None,
        )
        if flag_idx is not None and flag_idx + 1 < len(parts):
            sql_file = parts[flag_idx + 1]
            try:
                with open(sql_file) as fh:
                    return fh.read()
            except OSError:
                return None
        return None
    remaining = parts[1:]
    if len(remaining) >= 2:
        return remaining[1]
    return None


def validate_sql(sql: str) -> tuple[bool, str]:
    stripped = sql.strip().rstrip(";").strip()

    if not stripped:
        return True, ""

    if ";" in stripped:
        return False, (
            "Multi-statement SQL is not allowed.\n"
            "Submit one statement at a time.\n\n"
            f"Blocked SQL:\n{sql}"
        )

    if not SAFE_PREFIXES.match(stripped):
        return False, (
            "Query does not start with SELECT/WITH/EXPLAIN/SHOW.\n"
            "Only read-only queries are allowed.\n\n"
            f"Blocked SQL:\n{sql}"
        )

    match = BLOCKED_KEYWORDS.search(stripped)
    if match:
        keyword = match.group(0).upper()
        return False, (
            f"Query contains blocked keyword: {keyword}\n"
            "Only read-only queries are allowed.\n\n"
            f"Blocked SQL:\n{sql}"
        )

    return True, ""


def _block(message: str) -> None:
    result = {
        "hookSpecificOutput": {"permissionDecision": "deny"},
        "systemMessage": message,
    }
    print(json.dumps(result), file=sys.stderr)
    sys.exit(2)


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    command = input_data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    if "psycopg2" in command or (
        POSTGRES_CONN_RE.search(command)
        and not any(_is_db_sh(p) for p in command.split())
    ):
        _block(
            "BLOCKED: Direct database connection via psycopg2 or postgres:// URL "
            "is not allowed.\n"
            "Database writes are NEVER permitted. For read-only queries use "
            f"{DB_SH_PATH}.\n"
            "If database writes are needed, provide the SQL to the user to run manually."
        )

    script_match = re.search(
        r"(?:uv run(?:\s+--script)?|python3?)\s+(\S+\.py)", command
    )
    if script_match:
        script_path = script_match.group(1)
        try:
            with open(script_path) as fh:
                script_content = fh.read()
            if "psycopg2" in script_content or (
                POSTGRES_CONN_RE.search(script_content)
            ):
                _block(
                    f"BLOCKED: {script_path} contains direct database access "
                    "(psycopg2 or postgres:// URL).\n"
                    "Database writes are NEVER permitted. For read-only queries use "
                    f"{DB_SH_PATH}.\n"
                    "If database writes are needed, provide the SQL to the user "
                    "to run manually."
                )
        except OSError:
            pass

    for seg in _split_pipe_segments(command):
        seg = seg.strip()
        try:
            seg_parts = shlex.split(seg)
        except ValueError:
            seg_parts = []
        if seg_parts and _is_psql_binary(seg_parts[0]):
            _block(
                "BLOCKED: Direct psql calls are not allowed. "
                f"Use {DB_SH_PATH} instead.\n"
                f"Example: {DB_SH_PATH} mydb "
                '"SELECT count(*) FROM my_table"'
            )

    sql = extract_sql_from_command(command)
    if sql is None:
        sys.exit(0)

    ok, err = validate_sql(sql)
    if ok:
        sys.exit(0)

    _block(
        f"BLOCKED by db safety hook: {err}\n\n"
        "This query modifies data and cannot be run through the "
        "read-only tool. Print the SQL for the user to run manually."
    )


if __name__ == "__main__":
    main()
