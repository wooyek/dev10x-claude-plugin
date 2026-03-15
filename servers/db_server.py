#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp>=1.0"]
# ///

"""MCP server for database operations (read-only)."""

import json
import re
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Add lib directory to path for imports
lib_path = Path(__file__).parent / "lib"
import sys

sys.path.insert(0, str(lib_path))
from subprocess_utils import run_script

server = FastMCP(name="dev10x-db")


def is_read_only_sql(sql: str) -> bool:
    """Check if SQL statement is read-only (SELECT only).

    Args:
        sql: SQL statement to validate

    Returns:
        True if statement is read-only (SELECT), False otherwise
    """
    # Remove leading/trailing whitespace and comments
    sql_clean = re.sub(r"^\s*(--.*)?", "", sql, flags=re.MULTILINE).strip()

    # Check if it starts with SELECT (case-insensitive)
    if not re.match(r"^select\s", sql_clean, re.IGNORECASE):
        return False

    # Check for write operations in WITH clauses or subqueries
    # This is a simple heuristic - more sophisticated parsing could be added
    forbidden_keywords = [
        r"\bINSERT\b",
        r"\bUPDATE\b",
        r"\bDELETE\b",
        r"\bDROP\b",
        r"\bTRUNCATE\b",
        r"\bALTER\b",
        r"\bCREATE\b",
    ]

    for keyword in forbidden_keywords:
        if re.search(keyword, sql_clean, re.IGNORECASE):
            return False

    return True


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
            "error": "Write operations are prohibited. Only SELECT statements are allowed.",
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
