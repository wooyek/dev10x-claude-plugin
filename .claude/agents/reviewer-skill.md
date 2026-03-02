# Skill Reviewer

Review skill definitions for structure, naming convention, and
completeness.

## Trigger

Files matching: `skills/**`

## Required Reading

- `.claude/rules/skill-naming.md` — naming convention

## Checklist

1. **SKILL.md exists** — every skill directory must contain a SKILL.md with
   valid YAML front matter. Required: `name:`, `description:`. Optional:
   `invocation-name:`, `allowed-tools:`, `user-invocable:`.
2. **Naming convention** — directory uses plain name (no `dx-`
   prefix); invocation name uses `dx:<feature>` format or
   `dx:<family>:<skill>` for grouped families (see `skill-naming.md`)
3. **Description quality** — `description:` must explain when to
   trigger the skill; vague descriptions reduce discoverability
4. **Script references** — if SKILL.md references scripts, verify
   they exist in the skill directory
5. **Executable permissions** — directly-invoked scripts must be
   executable; `git ls-files --stage <path>` mode `100644` = not executable.
6. **Error handling** — scripts should use `set -e` and handle
   missing dependencies gracefully
7. **No hardcoded paths** — scripts should use relative paths or
   environment variables, not absolute user-specific paths
8. **`allowed-tools` coverage** — if SKILL.md calls external scripts,
   front matter must declare matching `Bash(...)` entries (missing entries
   cause per-invocation approval prompts); declared entries must not
   reference `~/.claude/` or other user-specific absolute paths.
9. **Template consistency** — YAML code blocks containing a `name:` field
   must follow `skill-naming.md`, not ad-hoc examples.
10. **Reference doc consistency** — cross-check `references/` documents
    against any matching `.claude/rules/` file.
11. **Embedded shell templates** — POSIX-compatible, no silent `|| true`,
    `<>` placeholder markers for user-replaceable values.
12. **Self-contained content** — no ephemeral references: no "(see
    Memory note...)", no "as discussed", no session-specific links;
    all constraints must be documented inline.

## Output Format

Apply to ALL `skills/**` files in the diff, including same-PR additions
(new checklist items are not retroactively applied to them otherwise).
For each issue: **File** · **Severity** (CRITICAL/WARNING/INFO) · **Issue**
