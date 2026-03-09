# PR Metadata Reviewer

Review pull request metadata for compliance with format standards.

## Severity Distinction

See `references/review-checks-common.md` for enforcement-level guidance.

## Trigger

All PRs (not file-scoped). Inspect PR body, branch name, and commits.

## Required Reading

- `references/git-pr.md` — PR body format and examples
- `references/git-commits.md` — commit message structure

## Checklist

1. **JTBD as first element** — Job Story must be the absolute first
   paragraph of PR body; no headers, bullets, or separators before it.
   Failure blocks release notes parsing. (REQUIRED)

2. **No separator between JTBD and commits** — The horizontal separator
   (`---`) must not appear between JTBD and commit list. Use only blank
   lines per `references/git-pr.md` format. (REQUIRED)

3. **Fixes link present and last** — `Fixes:` must be the absolute final
   line of PR body. No blank lines, separators, or additional text after
   it. (REQUIRED)

4. **Branch naming convention** — Branch must match
   `username/TICKET-ID/slug` or `username/slug` for self-motivated work.
   Worktrees: `username/TICKET-ID/worktree-name/slug`. (RECOMMENDED)

5. **Commits atomic and focused** — Each commit describes one logical
   change; commit titles use gitmoji + outcome-focused language per
   `references/git-commits.md`. (RECOMMENDED)

## Output Format

For each issue:
- **File**: N/A (PR metadata issue)
- **Severity**: REQUIRED or RECOMMENDED
- **Issue**: what's wrong
