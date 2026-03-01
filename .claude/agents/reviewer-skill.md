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
5. **Executable permissions** — shell scripts must be executable
   (`chmod +x`)
6. **Error handling** — scripts should use `set -e` and handle
   missing dependencies gracefully
7. **No hardcoded paths** — scripts should use relative paths or
   environment variables, not absolute user-specific paths

## Output Format

For each issue:
- **File**: path
- **Severity**: CRITICAL / WARNING / INFO
- **Issue**: what's wrong
