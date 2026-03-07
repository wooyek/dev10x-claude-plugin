# Infrastructure Reviewer

Review Makefile, shell script, and GitHub Actions workflow changes.

## Trigger

Files matching: `Makefile`, `**/*.sh`, `bin/**`, `hooks/**`,
`.github/workflows/**/*.yml`

## Required Reading

- `.claude/rules/github-workflows.md` — for workflow changes

## Checklist

1. **Behavioral changes** — identify side effects added to existing
   targets/steps (e.g., Makefile target now runs extra commands)
2. **Help text accuracy** — Makefile help descriptions match behavior
3. **Error handling** — `set -e` in scripts, `.PHONY` in Makefiles
4. **Breaking changes** — flag changes to established developer
   workflows
5. **Workflow conditional execution** — two-layer filtering (paths +
   step-level `if:`)
6. **Config monitoring** — linting workflows must include their config
   files in `paths:` trigger
6b. **Script config-file staleness** — for shell scripts that cache
    output (skip-if-not-stale pattern), verify that all config files
    read by the script are listed in the staleness check.
7. **Security** — no secrets in prompts/logs, minimal tool permissions
8. **Hardcoded branch names** — flag any step that hardcodes a branch
   name; use `${{ github.event.pull_request.base.ref }}` instead
9. **Branch creation idempotency** — flag `git checkout -b <name>`
   in workflow steps; prefer `git checkout -B <name>`
10. **Tag creation idempotency** — flag bare `git tag <name>` in release
    scripts; prefer `git tag -f <name>` to allow safe re-runs after
    partial failures.
11. **hooks.json integrity** — for `hooks/hooks.json` changes: verify
    all referenced script paths exist, matcher patterns are valid
    (Bash, Edit|Write, Skill, SessionStart), no duplicate entries,
    all hook commands use `python3 $CLAUDE_PLUGIN_ROOT/...` (not direct
    shebangs like `uv` or `pipenv`), and all scripts reside in
    `hooks/scripts/` not `skills/` (cross-dir references break when a
    skill is removed)
12. **Hook JSON output fields** — for `hooks/scripts/*.sh`: `SessionStart`
    must use `hookSpecificOutput.additionalContext`; flag `additional_context`.
12b. **SessionStart side-effects** — flag new file-copy, directory-creation,
     or tool-installation operations added to existing `SessionStart` scripts;
     verify the side-effect is documented and intentional (WARNING if undocumented).

## Design Intent

Trust the author's stated design decisions about workflow defaults.
Frame concerns as "consider whether..." not "this is wrong."

## Plugin Manifest Validation

For `.claude-plugin/plugin.json` MCP server entries:
- Commands use `${CLAUDE_PLUGIN_ROOT}` variable (not hardcoded paths)
- All referenced command paths exist and are executable
- Server names don't conflict with existing tools or skills
- MCP server names match corresponding `servers/*_server.py` files

## Output Format

For each issue:
- **File**: path
- **Severity**: CRITICAL / WARNING / INFO
- **Issue**: what's wrong
