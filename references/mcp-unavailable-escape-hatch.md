# MCP Server Unavailable — Escape Hatch

Canonical guidance when a `plugin:Dev10x:cli` MCP tool is
disconnected mid-session.

## Problem

When the MCP server disconnects, several skills end up in a
lose-lose loop:

1. The preferred MCP tool (e.g., `mcp__plugin_Dev10x_cli__push_safe`)
   fails because the tool is listed as "no longer available" in the
   system-reminder.
2. Older skill docs instruct the agent to fall back to a wrapper
   script (e.g., `git-push-safe.sh`).
3. The wrapper is blocked by `validate-bash-command.py` with
   "use the MCP tool instead" — because the wrapper itself is
   designed to redirect back to MCP.
4. Raw CLI (`git push`) is blocked by the same hook with
   "use Skill(Dev10x:git)".
5. Prefixing with `DEV10X_SKIP_CMD_VALIDATION=true` is rejected —
   the flag is reserved for skill-authorized exceptional cases,
   not transient MCP unavailability.

## Correct Response

**STOP and ask the user to reconnect the MCP server.**

Do NOT:
- Fall back to the wrapper script (blocked by hook)
- Fall back to the raw CLI (blocked by hook)
- Prefix with `DEV10X_SKIP_CMD_VALIDATION=true`
- Keep retrying the unavailable tool

Do instead:
- Say: "The `plugin:Dev10x:cli` MCP server is disconnected.
  Please reconnect it via `/mcp` or restart the session, then
  I will retry."
- Wait for the user to reconnect before proceeding.

## Detection

The MCP server is disconnected when:
- A `mcp__plugin_Dev10x_cli__*` tool call returns an error with
  "no longer available" or "tool not found"
- The system-reminder lists the tool under "no longer available"
- Multiple MCP calls fail in sequence with connection errors

## Affected Skills

Skills that invoke `Dev10x_cli` MCP tools and have wrapper
fallbacks in their documentation:

- `Dev10x:git` — `git-push-safe.sh`
- `Dev10x:git-fixup` — raw `gh api`
- `Dev10x:git-commit` — `mktmp` wrapper
- `Dev10x:git-groom` — raw git commands
- `Dev10x:gh-pr-create` — `create-pr.sh`, `verify-state.sh`
- `Dev10x:gh-pr-monitor` — `pr-notify.py`, `ci-check-status.py`
- `Dev10x:gh-pr-respond` — raw `gh api`
- `Dev10x:gh-pr-fixup` — raw `gh api`
- `Dev10x:gh-pr-triage` — raw `gh api`

All of the above should treat MCP unavailability as a hard stop,
not a signal to chain through wrapper fallbacks.

## Hook Reinforcement

The `skill_redirect` validator appends a standardized
`MCP_UNAVAILABLE_HINT` to every `use-tool` block message. When
the agent hits the hook while trying a wrapper or raw CLI, the
block message reminds them to ask the user to reconnect rather
than reach for `DEV10X_SKIP_CMD_VALIDATION`.

See `src/dev10x/validators/skill_redirect.py:MCP_UNAVAILABLE_HINT`.
