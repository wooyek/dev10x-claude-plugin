# PR Merge Policy: REQUIRED vs RECOMMENDED Feedback

How code review feedback is classified and whether it blocks merge.

## Feedback Classification

### REQUIRED Feedback

Marked with **REQUIRED:**, these items must be addressed before merge can proceed.

- **When enforced**: Merge is blocked until REQUIRED items are addressed
- **How to address**:
  - Create commits that fix the issue
  - Reply to comment with commit SHA
  - Author pushes changes; feedback is re-verified
- **If unaddressed**: PR cannot merge; reviewer or author must resolve before approval

**Example REQUIRED items**:
- PR body format violations (missing JTBD, missing `Fixes:` link, disallowed separators)
- Commit message format errors (missing gitmoji, ticket ID)
- Code conflicts with codebase conventions
- False positives verified by author response

### RECOMMENDED Feedback

Marked with **RECOMMENDED** or presented without explicit enforcement marker, these items are suggestions.

- **When applied**: Author may acknowledge, defer, or address per judgment
- **How to handle**:
  - Author may fix (create fixup commit)
  - Author may reply explaining deferral
  - Merge proceeds with or without addressing
- **If unaddressed**: Merge is allowed; no blocking

**Example RECOMMENDED items**:
- Suggestion to refactor for clarity (not correctness)
- Optional enhancement ideas
- Nice-to-haves flagged for future work
- Informational context

## Review Workflow

1. **Initial review** — Claude or maintainer posts feedback
2. **Author responds** — Creates fixup commits or replies to comments
3. **Force-push** — Feedback is re-verified after author pushes changes
4. **Re-review check** — On force-push, all feedback is re-evaluated
5. **Merge gate** — REQUIRED items must be addressed; RECOMMENDED may remain

## Frictionless Merge Feature

The `gh pr merge` feature (available after PR #455) enables one-command merge without web UI.

- **Impact**: Reduces friction but makes format compliance critical
- **Enforcement**: CI checks validate PR body format before merge is allowed
- **Responsibility**: Author must ensure REQUIRED feedback is addressed

## When Feedback is Re-Checked

Feedback is re-evaluated in these scenarios:

- **Force-push**: When author pushes new commits (common after fixup squash)
- **Author comment**: When author replies to explain changes
- **Manual request**: When reviewer requests another review pass

Feedback is **not** automatically re-checked after simple file edits or
approvals — it requires a commit push to re-trigger.

## References

- PR body format rules: `references/git-pr.md` § PR Body
- Commit format rules: `references/git-commits.md`
- Job Story format: `references/git-jtbd.md` § Voice Requirement
