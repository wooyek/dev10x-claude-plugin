# MCP Tool Naming and Invocation

Central reference for MCP tool naming conventions and invocation patterns.

## Name Format

MCP tools follow a consistent naming convention from Python function to MCP
registration:

- **Python function**: `snake_case` (e.g., `detect_tracker`)
- **MCP registration**: `mcp__plugin_<PluginName>_<ServerName>__<snake_case>`
  - `<PluginName>`: Title-case plugin name from plugin.json (e.g., `Dev10x`)
  - `<ServerName>`: Server name in plugin.json (e.g., `gh`, `git`, `db`)
  - `<snake_case>`: Unchanged function name

## Examples

| Server | Function | MCP Name |
|--------|----------|----------|
| `gh` | `detect_tracker()` | `mcp__plugin_Dev10x_gh__detect_tracker` |
| `gh` | `pr_comments()` | `mcp__plugin_Dev10x_gh__pr_comments` |
| `git` | `get_commit_log()` | `mcp__plugin_Dev10x_git__get_commit_log` |
| `db` | `list_tables()` | `mcp__plugin_Dev10x_db__list_tables` |
| `utils` | `mktmp()` | `mcp__plugin_Dev10x_utils__mktmp` |

## Tool Declaration Pattern

All MCP tools must follow this structure:

```python
@server.tool()
async def function_name(param: str, optional: str | None = None) -> dict:
    """Brief description of what the tool does."""
    # implementation
    if error_occurs:
        return {"error": "descriptive message"}
    return {tool-specific fields}  # see examples below
```

**Important**: Error responses are uniform (`{"error": msg}`), but success
responses are **tool-specific**. Document your tool's return structure in
its docstring. Examples:
- `mktmp`: returns `{"path": "/tmp/file"}`
- Some tools return `{"success": True, "data": result}`
- Some tools return only tool-specific fields without a `success` flag

Callers must know each tool's specific success response format.

## Tool Availability by Plugin Version

MCP tools are added incrementally. Document the minimum plugin version
supporting each tool:

| Tool | Server | Purpose | Availability |
|------|--------|---------|--------------|
| `mktmp` | `utils` | Create temp namespace directories | Available in all current versions |
| `push_safe` | `git` | Safely push branches (guards main/develop) | Available in all current versions |
| `rebase_groom` | `git` | Interactive rebase sequencer | Available in all current versions |
| `create_worktree` | `git` | Create isolated git worktrees | Available in all current versions |
| `detect_tracker` | `gh` | Detect issue tracker type (GH-, TEAM-, TT-, etc.) | Available in all current versions |
| `pr_detect` | `gh` | Extract PR context from number/URL/branch | Available in all current versions |
| `issue_get` | `gh` | Fetch issue details and metadata | Available in all current versions |
| `issue_comments` | `gh` | Fetch or manage issue comments | Available in all current versions |
| `pr_comments` | `gh` | Fetch, add, edit, or delete PR comments | Available in all current versions |
| `request_review` | `gh` | Request reviewers on a PR | Available in all current versions |
| `query` | `db` | Execute read-only SQL queries (SELECT only) | Available in all current versions |

When adding a new tool, update this table and note any dependencies on
specific CLI commands or external programs. Skills should declare required
tools explicitly in `allowed-tools:` to catch availability mismatches early.

## Skill Usage

In SKILL.md, declare MCP tool access via `allowed-tools:`:

```yaml
allowed-tools:
  - mcp__plugin_Dev10x_gh__detect_tracker
  - mcp__plugin_Dev10x_gh__pr_comments
  - Bash(/path/to/script:*)
```

Use wildcard sparingly: `mcp__plugin_Dev10x_gh__*` grants access to all gh
server tools. Prefer explicit tool names for security and clarity.

## Server Registration

Each MCP server must be registered in `.claude-plugin/plugin.json`:

```json
"mcpServers": {
  "gh": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/gh_server.py",
    "env": { "PYTHONUNBUFFERED": "1" }
  }
}
```

- Use `${CLAUDE_PLUGIN_ROOT}` for relative paths (not hardcoded paths)
- Server names must not conflict with existing tool or skill names
- All referenced command paths must exist and be executable
