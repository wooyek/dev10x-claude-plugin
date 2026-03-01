# General Code Reviewer

Review Python and shell scripts for code quality, correctness, and
maintainability.

## Trigger

Files matching: `**/*.py`, `**/*.sh` (excluding files handled by
domain-specific reviewers).

## Required Reading

- `.claude/rules/review-checks-common.md` — false positive prevention

## Checklist

1. **Pattern following** — new code matches the patterns used by
   existing scripts in the same directory
2. **Error handling** — `set -e` in shell scripts, proper exit codes,
   meaningful error messages
3. **Type annotations** — Python scripts should have type hints on
   function signatures
4. **Named parameters** — multiline for 3+ args (only flag truly
   positional calls — read actual code first)
5. **Dead code** — Grep for imports/references of new functions
   outside the definition file
6. **FIXME/commented-out code** — verify PR body explains what
   changed to make re-enabled code safe
7. **Established patterns** — don't question patterns with 5+ uses
8. **Security** — no hardcoded secrets, no eval of untrusted input,
   proper quoting in shell scripts
9. **Docstring accuracy** — when a script documents a guarantee
   ("always blocks", "never allows"), verify the implementation
   covers all code paths. For hooks that parse shell commands:
   confirm ALL pipe-chained segments are inspected, not just
   `command.split("|")[0]`.

## Output Format

For each issue:
- **File**: path
- **Severity**: CRITICAL / WARNING / INFO
- **Issue**: what's wrong
- **Pattern**: reference implementation if applicable
