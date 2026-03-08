#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp>=1.0"]
# ///

"""MCP server for general utilities (temp files, etc.)."""

from pathlib import Path
from mcp.server.fastmcp import FastMCP

lib_path = Path(__file__).parent / "lib"
import sys

sys.path.insert(0, str(lib_path))
from subprocess_utils import run_script

server = FastMCP(name="dev10x-utils")


@server.tool()
async def mktmp(
    namespace: str,
    prefix: str,
    ext: str = "",
    directory: bool = False,
) -> dict:
    """Create a unique temp file or directory under /tmp/claude/<namespace>/.

    Args:
        namespace: Subdirectory under /tmp/claude/ (e.g., "git", "skill-audit")
        prefix: Filename prefix (e.g., "commit-msg", "pr-review")
        ext: File extension including dot (e.g., ".txt", ".json"). Ignored for directories.
        directory: If True, create a directory instead of a file.

    Returns:
        Dictionary with key: path (str) — the created temp file/directory path
    """
    args = []
    if directory:
        args.append("-d")
    args.extend([namespace, prefix])
    if ext and not directory:
        args.append(ext)

    result = run_script("bin/mktmp.sh", *args)

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return {"path": result.stdout.strip()}


if __name__ == "__main__":
    server.run()
