# Skill Reviewer

Review skill definitions for structure, naming convention, and
completeness.

## Trigger

Files matching: `skills/**`

## Required Reading

- `.claude/rules/skill-naming.md` — naming convention

## Checklist

1. **SKILL.md exists** — every skill directory must contain a
   SKILL.md with valid YAML front matter (`name:`, `description:`)
2. **Naming convention** — directory uses plain name (no `dx-`
   prefix); invocation name uses `dx:<feature>` format
3. **Description quality** — `description:` must explain when to
   trigger the skill; vague descriptions reduce discoverability
4. **Script references** — if SKILL.md references scripts, verify
   they exist in the skill directory
5. **Executable permissions** — all scripts (shell and Python)
   invoked directly must be executable (`chmod +x`). Verify with
   `git ls-files --stage <path>` — mode `100644` means not executable.
6. **Error handling** — scripts should use `set -e` and handle
   missing dependencies gracefully
7. **No hardcoded paths** — scripts should use relative paths or
   environment variables, not absolute user-specific paths
8. **allowed-tools paths** — `Bash(...)` entries in SKILL.md front
   matter must not reference `~/.claude/` or other user-specific
   absolute paths; use plugin-relative paths or omit the path restriction
9. **Template consistency** — if SKILL.md contains a YAML code block
   with a `name:` field (a frontmatter template), verify it follows
   `skill-naming.md`, not an ad-hoc example
10. **Reference doc consistency** — if SKILL.md references a
    `references/` document that defines a process or format, check it
    for consistency with any matching `.claude/rules/` file

## Output Format

Apply this checklist to ALL `skills/**` files in the diff, including
any added in the same PR as rule changes — new checklist items are
not retroactively applied to same-PR additions otherwise.

For each issue:
- **File**: path
- **Severity**: CRITICAL / WARNING / INFO
- **Issue**: what's wrong
