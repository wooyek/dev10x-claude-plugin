#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp>=1.0"]
# ///

"""MCP server for database operations (read-only)."""

import json
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

lib_path = Path(__file__).parent / "lib"
sys.path.insert(0, str(lib_path))
from sql_validation import is_read_only_sql  # noqa: E402
from subprocess_utils import run_script  # noqa: E402

server = FastMCP(name="dev10x-db")


@server.tool()
async def query(
    database: str,
    sql: str,
) -> dict:
    """Execute a read-only SQL query against a database.

    Args:
        database: Database alias (pp, pos, ps, bp, backend, bs)
        sql: SELECT statement (write operations are blocked)

    Returns:
        Dictionary with keys: columns (list), rows (list of tuples), row_count (int)
    """
    # Validate that SQL is read-only
    if not is_read_only_sql(sql):
        return {
            "error": (
                "Write operations are prohibited. "
                "Only read-only queries (SELECT, WITH, EXPLAIN, SHOW) are allowed."
            ),
            "blocked": True,
        }

    # Call the db.sh wrapper script
    result = run_script("skills/db-psql/scripts/db.sh", database, sql)

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    # Try parsing as JSON
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        # If not JSON, return as raw output
        return {"raw_output": result.stdout}


if __name__ == "__main__":
    server.run()
