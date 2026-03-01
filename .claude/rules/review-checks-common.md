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

## Python Linting Checks

- **f-strings without expressions**: `f"static string"` with no `{}`
  placeholders is ruff F541. Flag and suggest removing the `f` prefix.
