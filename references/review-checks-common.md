# Review Checks — Cross-Cutting Concerns

Universal review checks regardless of domain-specific agent. For
workflow rules, see `review-guidelines.md`.

## False Positive Prevention Gate

Before posting **any** inline comment:

0. **Diff scope** — is this file changed in the current PR diff?
   Run `gh pr diff --name-only` to confirm. If not in diff, mark
   pre-existing and skip.
1. Does this violate a documented CLAUDE.md rule? (No rule = preference)
2. Does this contradict an established codebase pattern? (5+ uses)
3. Does referenced documentation file exist? (Verify with Read tool)
4. Quality improvement or just preference?

**If any answer fails, DO NOT post.**

## Code Verification Protocol

1. Read actual code file — never rely on diff snippets alone
2. Verify exact line numbers and values
3. Check for fixes in later commits
4. Quote exact code when making claims

## Known False-Positive Traps

Before raising any of these, **verify actual code**:

1. **Formatting already correct**: read current code, not diff context
2. **Code that no longer exists**: verify line exists after force-push
3. **Return type already present**: read the actual signature
4. **YAGNI**: accept author's "defer" judgment
5. **Rule file paths**: verify path exists with Glob before citing;
   correct paths listed in `.claude/rules/README.md`
6. **Intentional behavior removal**: when PR title/ticket states
   removal is intentional, external bots flagging it as a bug are
   false positives
7. **Re-raise after side-effect**: `except E: side_effect(); raise`
   is NOT swallowing — caller still receives the error
8. **Shell script style**: different scripts use different shells
   (bash, sh, fish) — check the shebang before flagging syntax
9. **Skill SKILL.md format**: `name:` and `description:` are YAML
   front matter, not arbitrary fields — don't suggest restructuring
10. **External user-level skill names**: before flagging invocation names not
    in this repo (e.g., `ticket:branch`), check if the author confirmed they
    are external skills at `~/.claude/skills/`. If confirmed, do NOT re-raise.
11. **`~/.claude/` in `allowed-tools`**: skills delegating to user-installed
    tools (`~/.claude/tools/`, `~/.claude/skills/`) legitimately use these
    paths. Only flag if the path belongs to a plugin-distributed script.
12. **`/pull/new/` commit links**: pre-creation artifacts generated before the
    PR number is assigned — flag as RECOMMENDED to update to
    `/pull/<number>/commits/<sha>`, not REQUIRED.
13. **Plugin-vs-user skill path conversions**: when a PR converts
    `~/.claude/skills/<name>/` to `${CLAUDE_PLUGIN_ROOT}/skills/<name>/`,
    verify each `<name>` directory actually exists in `skills/`. Use Glob:
    `skills/<name>/SKILL.md`. Non-existent directories are user-level skills
    — the `~/.claude/` prefix must be preserved.
14. **`invocation-name` with non-`dx:` prefix**: `invocation-name: ticket:foo`
    alongside `name: dx:ticket-foo` is valid. The `dx:` prefix requirement
    applies to `name:` only — do NOT flag `invocation-name:` as a naming
    violation when `name:` is already correct.
15. **Write-path namespace coverage** — when a `Write(/tmp/claude/<ns>/**)`
    entry is renamed, verify the new namespace matches the first argument of
    every `mktmp.sh` invocation in that SKILL.md. A mismatch causes a
    write-permission rejection at runtime.
16. **Ticket ID prefix (`GH-` vs bare number)**: examples in
    `references/git-commits.md` show both `GH-<N>` and bare numbers (e.g.
    `79`). Only flag format as REQUIRED if the project has an explicit rule —
    otherwise raise as RECOMMENDED at most.

## Parameter Change Analysis

When parameters are added/removed/made optional:
- Grep **all** call sites (not just the diff)
- Check if optional serves backward compatibility
- When suggesting required: list all call sites to confirm

## Dead Code Detection

For new classes/functions/constants in the PR:
- Grep for imports and references outside the definition file
- If no references found, flag as potential dead code
- Exclude test classes, abstract base classes, `__init__` exports

## Naming Convention Verification

Before suggesting naming changes:
1. Search codebase patterns first (5+ files = established convention)
2. Only suggest genuinely unclear/misleading names
3. Do NOT flag: established patterns, version suffixes, domain prefixes

## Module Architecture Awareness

Different skills and scripts may use different patterns intentionally.
Only flag security concerns, documented rule violations, or bugs —
not valid architectural choices.

## CLI Command Verification

When docs reference CLI commands (e.g., install instructions):
- Verify commands appear in `CLAUDE.md` Development section, or
- Confirm they are known Claude Code CLI built-ins
- Unverified commands in user-facing docs are WARNING severity

## Shell Anti-Patterns

- **Hardcoded temp paths**: skills must not hardcode `/tmp/claude/<x>.txt`.
  All temp files must be created via
  `${CLAUDE_PLUGIN_ROOT}/bin/mktmp.sh <namespace> <prefix> [.ext]`.
  Hardcoded paths are WARNING; missing `allowed-tools` coverage is also WARNING
  (see rules 8b/8e in `reviewer-skill.md`).
- **Silent error swallowing**: `|| true` on setup steps and `2>/dev/null`
  on media-encoding commands (ffmpeg, convert, ImageMagick) hide failures;
  replace with a fallback action (`|| { cmd; }`) or remove the redirect.
  Also flag `2>/dev/null` on any command whose stdout is captured into a
  variable (`var=$(cmd 2>/dev/null)`) when that variable drives branching
  logic — an empty string from a silenced failure produces misleading errors
  downstream.
- **Pipe segment completeness in security hooks**: when a hook script
  parses a shell command to detect a pattern (e.g., `python3 -c`),
  it must inspect ALL pipe-delimited segments, not just
  `command.split("|")[0]`. Use `for seg in command.split("|"):` or
  mirror the `segments[1:]` loop pattern from existing hooks.

## Python Linting Checks

- **f-strings without expressions**: `f"static string"` with no `{}`
  placeholders is ruff F541. Flag and suggest removing the `f` prefix.
