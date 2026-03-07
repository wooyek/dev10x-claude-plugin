---
name: dev10x:gh-pr-triage
description: Validate a PR review comment against the codebase. If invalid, reply with evidence. Never auto-resolves threads — resolution requires explicit user confirmation. Returns a verdict (VALID, INVALID, QUESTION, OUT_OF_SCOPE) so the caller knows whether a code fix is needed.
user-invocable: true
invocation-name: dev10x:gh-pr-triage
allowed-tools:
  - Bash(~/.claude/tools/gh-pr-comments.py:*)
---

# Triage PR Review Comment

## Overview

This skill evaluates whether a PR review comment requires a code change by
investigating the codebase. It replies to non-valid comments with evidence but
never auto-resolves threads. Returns a verdict to the caller.

**Verdicts:**

| Verdict | Meaning | Action taken |
|---------|---------|-------------|
| `VALID` | Comment identifies a real issue needing a fix | None — caller handles |
| `INVALID` | Comment is factually wrong (code already correct) | Reply with evidence |
| `QUESTION` | Reviewer asking a question, no code change needed | Reply with answer |
| `OUT_OF_SCOPE` | Valid concern but beyond this PR's scope | Acknowledge |

**Thread resolution policy:** Never auto-resolve threads. Thread
resolution requires explicit user confirmation. The user supervising
the PR review needs resolved threads to remain visible so they can
verify the triage decisions without searching through hidden threads.

**When to use this skill:**
- Called by `dev10x:gh-pr-respond` before delegating to `dev10x:gh-pr-fixup`
- Standalone when you want to validate a comment without committing to a fix

## Orchestration

This skill follows `references/task-orchestration.md` patterns.

**Auto-advance:** Complete each step, immediately start the next.
Never pause to ask "should I continue?" between steps.

**Task tracking:** Create tasks for each step so the supervisor
can track progress:

```
TaskCreate(subject="Fetch comment context",
    activeForm="Fetching comment context")
TaskCreate(subject="Validate against codebase",
    activeForm="Validating against codebase")
TaskCreate(subject="Draft verdict and reply",
    activeForm="Drafting verdict")
```

Set dependencies: validate blocked by fetch, draft blocked by
validate.

## Input Requirements

1. **PR URL or Comment URL** — Full GitHub URL to the PR comment
   (e.g., `https://github.com/owner/repo/pull/123#discussion_r456`)
2. **Repository** — Owner/repo (extracted from URL or defaults to current repo)

**Optional additional context:**
- User may provide extra context after the URL
- Example: `/dev10x:gh-pr-triage https://...#discussion_r456 this is a Django project`

## Workflow

### Step 1: Parse Input and Fetch Comment

**Parse the comment URL:**
```
URL format: https://github.com/{owner}/{repo}/pull/{pr_number}#discussion_r{comment_id}
```

**Fetch the comment:**
```bash
~/.claude/tools/gh-pr-comments.py get --comment-id {comment_id}
```

Extract:
- `body` — The comment text
- `path` — File path the comment is on
- `line` / `original_line` — Line number in the diff
- `diff_hunk` — Code context around the comment
- `html_url` — Direct link
- `user.login` — Who left the comment
- `in_reply_to_id` — Parent comment (null for root comments)

### Step 2: Fetch All PR Threads

Check for previously addressed issues to avoid duplicate work:

```bash
~/.claude/tools/gh-pr-comments.py list --pr {pr_number} --root-only
```

Look for:
- Threads already resolved
- Threads with fixup commit references in replies
- Threads raising the same concern as this comment

### Step 3: Classify the Comment

Determine what type of comment this is:

| Type | Signals |
|------|---------|
| **Code suggestion** | "should use X", "change to Y", suggestion block |
| **Missing-feature claim** | "missing field/method/annotation" |
| **Pattern concern** | "should follow pattern X", "inconsistent with Y" |
| **Question** | Ends with `?`, starts with "why", "how", "what" |
| **Scope expansion** | "also consider", "might want to add", "future" |
| **Intentional design question** | "why not use X?", "why different from Y?" |

### Step 4: Investigate Using Validation Patterns

Load `references/validation-patterns.md` for the full catalog. Common
investigations:

**Inherited Field** — Reviewer claims a field/method is missing:
```
1. Read the file at the commented line
2. Find the class definition
3. Trace inheritance chain (check base classes, mixins)
4. If field/method exists in a parent → INVALID
```

**Existing Convention** — "Should use X instead of Y":
```
1. Grep codebase for both patterns X and Y
2. Count occurrences of each
3. If Y is the established pattern → INVALID
4. If X is more common → VALID (or QUESTION if close)
```

**Already Present** — "Missing type/annotation/test":
```
1. Read exact file + line range
2. Check if the claimed missing thing is already there
3. If present → INVALID with exact line reference
```

**Established Sibling** — "Change signature/return type":
```
1. Find all sibling implementations (same interface/pattern)
2. List their signatures
3. If current code matches siblings → INVALID
```

**Previously Addressed** — Same concern raised in other threads:
```
1. Search all PR threads for similar keywords
2. Check if a fixup commit already addressed it
3. If addressed → INVALID with thread URL reference
```

### Step 5: Render Verdict

Based on investigation, choose one of:

#### VALID — Real issue, needs a fix

Do nothing. Return verdict to caller (usually `dev10x:gh-pr-respond`) which will
delegate to `dev10x:gh-pr-fixup`.

**Output:**
```
Verdict: VALID
Reason: {brief explanation of why the comment is correct}
```

#### INVALID — Comment is factually wrong

Post an evidence-based reply. Do **NOT** resolve the thread.

**Reply format:**
```markdown
{evidence explanation}

{code snippet or grep results showing the evidence}
```

**Output:**
```
Verdict: INVALID
Reason: {brief explanation}
Action: Replied with evidence (thread left open for user to resolve)
```

#### QUESTION — No code change needed

Post a clear answer explaining the design decision or code behavior.
Do **NOT** resolve the thread.

**Reply format:**
```markdown
{answer to the question with context}
```

**Output:**
```
Verdict: QUESTION
Reason: {brief explanation}
Action: Replied with answer (thread left open for user to resolve)
```

#### OUT_OF_SCOPE — Valid but beyond this PR

Post a brief acknowledgment. Do **NOT** resolve the thread.

**Reply format:**
```markdown
Out of scope for this PR. {optional: brief reason or link to tracking ticket}
```

**Output:**
```
Verdict: OUT_OF_SCOPE
Reason: {brief explanation}
Action: Acknowledged (thread left open for user to resolve)
```

## Reply Mechanics

**Post reply in the thread (not top-level):**
```bash
gh api \
  --method POST \
  repos/{owner}/{repo}/pulls/{pr_number}/comments/{comment_id}/replies \
  -f body="{reply_text}"
```

**Thread resolution:** Do NOT resolve threads. Return the verdict to the
caller (`dev10x:gh-pr-respond` or the user). Resolution only happens when the user
explicitly confirms it — either via `dev10x:gh-pr-respond`'s confirmation flow or
by direct user request.

## Error Handling

### Comment Not Found
```
Error: Could not fetch comment {comment_id}.
Verify the comment ID and repository.
```

### Ambiguous Verdict
If investigation is inconclusive:
- Default to `VALID` (let the fix author decide)
- Log uncertainty: "Leaning VALID — investigation inconclusive"

### Thread Already Resolved
If the thread is already resolved, skip it:
```
Skipped: Thread already resolved
```

## Integration

```
dev10x:gh-pr-monitor → dev10x:gh-pr-respond (orchestrator)
                 ├── dev10x:gh-pr-triage         ← this skill
                 └── dev10x:gh-pr-fixup
                      └── commit:fixup
```

**Standalone usage:**
```bash
/dev10x:gh-pr-triage https://github.com/owner/repo/pull/123#discussion_r456
```

**Called by dev10x:gh-pr-respond:**
```
dev10x:gh-pr-respond receives comment URL
  → delegates to dev10x:gh-pr-triage
  → if VALID → delegates to dev10x:gh-pr-fixup
  → if INVALID/QUESTION/OUT_OF_SCOPE → dev10x:gh-pr-triage replied,
    dev10x:gh-pr-respond asks user to confirm thread resolution
```

## References

### references/validation-patterns.md

Contains the full catalog of validation patterns with detection heuristics
and investigation steps.

### references/github_api.md

Contains GitHub API documentation for:
- Listing PR comments
- Fetching single comments
- Creating replies
- Resolving review threads (GraphQL)
- Filtering and querying
