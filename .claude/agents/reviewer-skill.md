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
2. **Naming convention** — directory uses plain name (no `dx-` prefix);
   `name:` MUST use `dx:<feature>` format; `invocation-name:` MAY use
   a non-`dx:` prefix for cross-family aliases — do NOT flag as a
   naming violation if `name:` is correct (see `skill-naming.md`)
3. **Description quality** — `description:` must explain when to
   trigger the skill; vague descriptions reduce discoverability
4. **Script references** — SKILL.md-referenced scripts must exist in the
   directory. Check both `allowed-tools` entries AND inline code blocks.
   Pay special attention when a path conversion corrects a typo (e.g.,
   `skill:create` → `skill-create`) — the fix may reveal a pre-existing
   missing script.
5. **Executable permissions** — directly-invoked scripts must be
   executable; `git ls-files --stage <path>` mode `100644` = not executable.
6. **Error handling** — scripts use `set -e`; handle missing dependencies
7. **No hardcoded paths** — scripts should use relative paths or
   environment variables, not absolute user-specific paths
8. **`allowed-tools` coverage** — if SKILL.md calls external scripts,
   front matter must declare matching `Bash(...)` entries (missing entries
   cause per-invocation approval prompts). Plugin-distributed scripts must
   use relative paths; `~/.claude/tools/` or `~/.claude/skills/` paths
   are accepted for user-tool delegation, not portability violations.
8b. **`allowed-tools` sync** — when a PR adds `mktmp.sh <ns> ...` calls,
    verify BOTH entries are present: `Bash(${CLAUDE_PLUGIN_ROOT}/bin/mktmp.sh:*)`
    (covers the mktmp call) AND `Write(/tmp/claude/<ns>/**)` (covers writing
    the returned path). For other Bash calls to external scripts, confirm a
    matching `Bash(<path>:*)` entry exists. Missing either causes WARNING.
8e. **Shared helper propagation** — when a PR introduces or propagates a
    new `bin/<script>` helper across multiple skills, enumerate ALL changed
    SKILL.md files and verify each has a matching
    `Bash(${CLAUDE_PLUGIN_ROOT}/bin/<script>:*)` entry in `allowed-tools`.
    Do not rely on spotting individual occurrences — grep across the diff.
8c. **Plugin directory existence** — for every `${CLAUDE_PLUGIN_ROOT}/skills/<name>/`
    entry in `allowed-tools`, verify `skills/<name>/` exists using
    Glob(`skills/<name>/SKILL.md`). A missing directory means the skill is
    user-level; the path must stay as `~/.claude/skills/<name>/`.
8d. **Skill porting pattern** — when a PR converts `~/.claude/skills/<name>/`
    to `${CLAUDE_PLUGIN_ROOT}/skills/<name>/`, systematically verify:
    (a) all scripts have mode `100755` (`git ls-files --stage`)
    (b) all `allowed-tools:` entries cover every script invocation,
        including cross-skill delegations to other plugin skill directories
    (c) no hardcoded absolute paths — use `${VAR:-/default/path}`
9. **Template consistency** — YAML code blocks containing a `name:` field
   must follow `skill-naming.md`, not ad-hoc examples.
10. **Reference doc consistency** — cross-check `references/` documents
    against any matching `.claude/rules/` file.
10b. **Inline table consistency** — when SKILL.md contains a reference
     table (e.g., "Aliases Configured"), cross-check documented values
     against the script; mismatches are a reliable bug signal.
11. **Embedded shell templates** — POSIX-compatible, no silent `|| true`,
    `<>` placeholder markers for user-replaceable values.
11b. **Embedded Python templates** — Python code blocks inside SKILL.md that
     are generated into scripts must pass the same quality checks:
     - No duplicate imports (ruff F811)
     - No f-strings without expressions (ruff F541)
     - `os.environ[...]` for credentials, never hardcoded values
12. **Self-contained content** — no ephemeral references ("see Memory note",
    "as discussed"); all constraints documented inline.
13. **Bundled binaries** — if `skills/<name>/bin/` contains a non-script
    binary (`.jar`, `.exe`, compiled binary):
    - Verify license is compatible with the plugin's license
    - Flag size if > 1 MB (INFO severity)
    - Suggest README or SKILL.md install instructions as an alternative
      when the binary is publicly available and stable

## Output Format

Apply to ALL `skills/**` files in the diff, including same-PR additions
(new checklist items are not retroactively applied to them otherwise).
For each issue: **File** · **Severity** (CRITICAL/WARNING/INFO) · **Issue**
