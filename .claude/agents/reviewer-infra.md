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
7. **Security** — no secrets in prompts/logs, minimal tool permissions
8. **Hardcoded branch names** — flag any step that hardcodes a branch
   name; use `${{ github.event.pull_request.base.ref }}` instead
9. **Branch creation idempotency** — flag `git checkout -b <name>`
   in workflow steps; prefer `git checkout -B <name>`
10. **hooks.json integrity** — for `hooks/hooks.json` changes: verify
    all referenced script paths exist, matcher patterns are valid
    (Bash, Edit|Write, Skill, SessionStart), and no duplicate entries

## Design Intent

Trust the author's stated design decisions about workflow defaults.
Frame concerns as "consider whether..." not "this is wrong."

## Output Format

For each issue:
- **File**: path
- **Severity**: CRITICAL / WARNING / INFO
- **Issue**: what's wrong
