---
name: dev10x:gh-pr-respond
description: Validate and respond to PR review comments. Handles single comment (with follow-up offer) or batch mode for all unaddressed comments on a PR/review. Orchestrates dev10x:gh-pr-triage and dev10x:gh-pr-fixup.
user-invocable: true
invocation-name: dev10x:gh-pr-respond
allowed-tools:
  - Bash(gh:*)
  - Skill(dev10x:gh-pr-triage)
  - Skill(dev10x:gh-pr-fixup)
---

# Respond to PR Review Comments

## Orchestration

This skill follows `references/task-orchestration.md` patterns.

**Auto-advance:** Complete each step, immediately start the next.
Never pause to ask "should I continue?" between steps.

**REQUIRED: Create tasks before ANY work.** Execute these
`TaskCreate` calls at startup based on the detected mode:

**Mode A (single):**
1. `TaskCreate(subject="Process comment r{id}", activeForm="Processing comment")`
2. `TaskCreate(subject="Check remaining comments", activeForm="Checking remaining")`

**Mode B (batch):**
1. `TaskCreate(subject="Collect unaddressed comments", activeForm="Collecting comments")`
2. `TaskCreate(subject=f"Triage {N} comments", activeForm="Triaging comments")`
3. `TaskCreate(subject="Execute approved responses", activeForm="Executing responses")`
4. `TaskCreate(subject="Resolve threads", activeForm="Resolving threads")`

Set dependencies and update status as each completes.

**Parallel triage (Mode B Step 2):** Dispatch up to 4 triage
subagents concurrently to reduce processing time. Each subagent
receives only its comment context and returns verdict + draft
reply.

**Batched decisions:** Thread resolution decisions are queued
and presented as a batch after all responses are posted.

## Decision Gates

This skill has 4 **blocking decision gates** where execution
MUST pause for user input via the `AskUserQuestion` tool.

**Plain text questions are NOT acceptable** — they don't block
execution, don't provide clickable options, and break the
structured decision flow the user relies on.

| # | Location | Purpose |
|---|----------|---------|
| 1 | Mode A, Step 1b | Confirm thread resolution |
| 2 | Mode A, Step 3 | Continue / batch / stop |
| 3 | Mode B, Step 3 | Approve / review / skip batch |
| 4 | Mode B, Step 5 | Resolve threads confirmation |

Each gate is marked with **REQUIRED: `AskUserQuestion`** in the
step description. If you see that marker, you MUST call the
`AskUserQuestion` tool — never substitute with inline text.

## Overview

This skill handles PR review comments end-to-end in two modes:

1. **Single comment mode** — Given a specific comment URL, process that one
   comment, then check for remaining unaddressed comments and offer to continue.
2. **Batch mode** — Given a PR URL or review URL, collect all unaddressed
   comments, triage them, and present a response plan for user approval.

Sub-skills:
- **`dev10x:gh-pr-triage`** — Validate the comment against the codebase
- **`dev10x:gh-pr-fixup`** — Implement the fix if the comment is valid

```
dev10x:gh-pr-respond (this skill)
    ├── dev10x:gh-pr-triage         → validate, reply if invalid (never auto-resolves)
    ├── resolve gate      → ask user to confirm thread resolution
    └── dev10x:gh-pr-fixup  → implement fix, fixup commit, reply with ref
         └── commit:fixup → create the fixup! commit
```

## Input Detection

Parse the input URL to determine the mode:

| Input pattern | Mode | Example |
|---|---|---|
| `...pull/123#discussion_r456` | Single | Specific comment URL |
| `...pull/123#pullrequestreview-789` | Batch (review) | All comments from that review |
| `...pull/123` | Batch (PR) | All unaddressed comments on PR |
| PR number only (e.g., `1164`) | Batch (PR) | All unaddressed comments on PR |

Extract `{owner}`, `{repo}`, `{pr_number}`, and optionally `{comment_id}`
or `{review_id}` from the URL.

**Optional additional context:**
- User may provide extra context after the URL
- Example: `/dev10x:gh-pr-respond https://...#discussion_r456 Note that PR #1135 is merged`

---

## Mode A: Single Comment

**Trigger:** Input contains `#discussion_r{comment_id}`

### Step 1: Process the comment

Delegate to `dev10x:gh-pr-triage` with the comment URL (and any additional context).

`dev10x:gh-pr-triage` returns a verdict: `VALID`, `INVALID`, `QUESTION`, or `OUT_OF_SCOPE`.

- If **VALID** → delegate to `dev10x:gh-pr-fixup` to implement fix, commit, push,
  and reply.
- If **not VALID** → `dev10x:gh-pr-triage` has posted a reply but has NOT resolved the
  thread. Ask the user whether to resolve it (see Step 1b).

### Step 1b: Confirm thread resolution (non-VALID only)

When `dev10x:gh-pr-triage` returns INVALID, QUESTION, or OUT_OF_SCOPE, present the
verdict and reason to the user and ask for confirmation before resolving:

```
Comment r{comment_id} on {path}:{line}:
  Verdict: {verdict}
  Reason: {reason}
  Reply posted: ✅

Resolve this thread?
```

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
This blocks execution until the user responds. Options:
- **"Resolve"** — Resolve the thread via GraphQL
- **"Leave open"** — Keep the thread open (reply already posted)

### Step 2: Check for remaining comments

After processing the single comment, check for other unaddressed root comments:

```bash
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments \
  | jq '[.[] | select(.in_reply_to_id == null)]'
```

### Step 3: Offer to continue

If unaddressed comments remain, present them to the user:

```
Processed comment r{comment_id} → {verdict}

{N} unaddressed comment(s) remaining:
1. {author} on {path}:{line} — "{first_line_of_body}"
2. {author} on {path}:{line} — "{first_line_of_body}"

Continue to the next one?
```

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
This blocks execution until the user decides how to proceed. Options:
- **"Next comment"** — Process the next unaddressed comment (loop back to Step 1)
- **"Switch to batch mode"** — Triage all remaining and present a plan (jump to Mode B Step 2)
- **"Stop"** — End

---

## Mode B: Batch (PR or Review)

**Trigger:** Input is a PR URL, review URL, or PR number (no `#discussion_r`)

### Step 1: Collect unaddressed comments

**For a PR URL or number:**
```bash
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments \
  | jq '[.[] | select(.in_reply_to_id == null)]'
```

**For a review URL** (`#pullrequestreview-{review_id}`):
Filter to only comments from that review (match `pull_request_review_id`).

If no unaddressed comments found → report "No unaddressed comments" and stop.

### Step 2: Triage all comments (parallel)

Mark phase transition: `TaskUpdate(taskId=triage_task, status="in_progress")`

Dispatch parallel triage subagents — up to 4 concurrent. Each
subagent receives only its comment context (not the full PR diff)
and returns only the verdict + draft reply:

```
# In a single tool-call block:
Agent(description=f"Triage r{id1} on {path1}",
    prompt=f"""Triage PR comment r{id1}:
    File: {path1}:{line1}
    Comment: "{body1}"
    Code context: {surrounding_code}
    Evaluate: VALID, INVALID, QUESTION, or OUT_OF_SCOPE?
    Return: verdict, reason (1 sentence), draft reply (2-3 sentences).""",
    run_in_background=true)
Agent(description=f"Triage r{id2} on {path2}", ..., run_in_background=true)
Agent(description=f"Triage r{id3} on {path3}", ..., run_in_background=true)
Agent(description=f"Triage r{id4} on {path4}", ..., run_in_background=true)
```

Collect results as notifications arrive. If more than 4 comments,
dispatch the next batch as agents complete.

Mark phase transition: `TaskUpdate(taskId=triage_task, status="completed")`

Present the full plan to the user as a table:

```
Found {N} unaddressed comments on PR #{pr_number}:

| # | Author | File:Line | Summary | Verdict | Proposed Response |
|---|--------|-----------|---------|---------|-------------------|
| 1 | mike   | sender.py:19 | Use SubFactory | VALID | Change LazyFunction → SubFactory |
| 2 | mike   | fakers.py:21 | Randomize values | VALID | Use Faker() for all fields |
| 3 | claude[bot] | dto.py:5 | TYPE_CHECKING | INVALID | 38+ files use this pattern |
| 4 | claude[bot] | tasks.py:12 | Missing type ann | INVALID | mypy infers from assignment |

Approve all, or specify which to modify/skip?
```

### Step 3: Get user approval

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
This blocks execution until the user approves the batch plan. Options:
- **"Approve all"** — Execute all proposed responses
- **"Review one-by-one"** — Present each for individual approval (like Mode A)
- **"Skip"** — Cancel batch

The user may also provide corrections in free text (e.g., "Comment 2 is not
valid, we use DataclassField" or "Comment 4: make it a question to the
reviewer").

### Step 4: Execute approved responses

Mark phase transition: `TaskUpdate(taskId=execute_task, status="in_progress")`

For each approved comment:

- **VALID** → delegate to `dev10x:gh-pr-fixup` (one fixup commit per comment)
- **INVALID / QUESTION / OUT_OF_SCOPE** → post reply using `gh api`:
  ```bash
  gh api --method POST \
    repos/{owner}/{repo}/pulls/{pr_number}/comments/{id}/replies \
    -f body="{reply}"
  ```
  Do **NOT** resolve the thread automatically.

Report progress after each comment is processed.

Mark phase transition: `TaskUpdate(taskId=execute_task, status="completed")` then `TaskUpdate(taskId=resolve_task, status="in_progress")`

### Step 5: Thread resolution confirmation

After all replies are posted for non-VALID comments, collect threads that
could be resolved and present them individually to the user for confirmation.

**CRITICAL: Never auto-resolve threads.** The user supervising the PR review
needs to verify each triage decision. Auto-resolving hides threads on GitHub,
forcing the user to search through collapsed conversations.

Present each thread with its verdict and reason:

```
{N} threads replied to but not yet resolved:

1. r{id} on {path}:{line} — {verdict}: {reason}
   → Reply posted: "{first_line_of_reply}..."

2. r{id} on {path}:{line} — {verdict}: {reason}
   → Reply posted: "{first_line_of_reply}..."

Resolve these threads?
```

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
This blocks execution until the user confirms which threads
to resolve. Options:
- **"Resolve all"** — Resolve all listed threads
- **"Review one-by-one"** — Confirm each thread individually
- **"Leave all open"** — Keep all threads open (replies already posted)

**If "Review one-by-one":** For each thread, present:
```
r{id} on {path}:{line}
  Verdict: {verdict}
  Reason: {reason}
  Reply: "{reply_excerpt}"

Resolve this thread?
```
Options: "Resolve" / "Leave open"

**After confirmation**, resolve only the user-approved threads via GraphQL.

### Step 6: Summary

After all comments are processed, report:

```
Batch complete: {N} comments processed
- {x} VALID (fixup commits created)
- {y} INVALID (replied)
- {z} QUESTION (answered)
- {w} OUT_OF_SCOPE (acknowledged)
- {r} threads resolved (user-confirmed)
- {u} threads left open
```

---

## Tools

Use `gh api` for PR comment operations:

| Operation | Command |
|---|---|
| List comments | `gh api repos/{owner}/{repo}/pulls/{N}/comments` |
| Filter root only | `\| jq '[.[] \| select(.in_reply_to_id == null)]'` |
| Fetch one comment | `gh api repos/{owner}/{repo}/pulls/comments/{id}` |
| Reply to thread | `gh api --method POST repos/{owner}/{repo}/pulls/{N}/comments/{id}/replies -f body="..."` |
| Resolve thread | See `references/github_api.md` GraphQL section |

---

## Decision Flow

```
Input URL
    │
    ├─ Has #discussion_r{id} ──► MODE A (single)
    │       │
    │       ├── dev10x:gh-pr-triage → verdict
    │       ├── if VALID → dev10x:gh-pr-fixup
    │       ├── if not VALID → reply posted, ask user to resolve
    │       ├── check remaining
    │       └── offer: next / batch / stop
    │
    └─ PR URL / review URL / number ──► MODE B (batch)
            │
            ├── collect unaddressed comments
            ├── triage all (draft, don't post)
            ├── present plan table
            ├── get user approval
            ├── execute approved responses (reply only, no resolve)
            ├── collect non-VALID threads → ask user to confirm resolution
            └── summary
```

## Integration

```
dev10x:gh-pr-monitor → dev10x:gh-pr-respond (this skill)
                 ├── dev10x:gh-pr-triage
                 └── dev10x:gh-pr-fixup
                      └── commit:fixup
```

**Standalone usage:**
```bash
# Single comment
/dev10x:gh-pr-respond https://github.com/owner/repo/pull/123#discussion_r456

# Single comment with context
/dev10x:gh-pr-respond https://github.com/owner/repo/pull/123#discussion_r456 Note that PR #1135 is merged

# Batch — all unaddressed comments on PR
/dev10x:gh-pr-respond https://github.com/owner/repo/pull/123

# Batch — all comments from a specific review
/dev10x:gh-pr-respond https://github.com/owner/repo/pull/123#pullrequestreview-789

# Batch — PR number only
/dev10x:gh-pr-respond 1164
```

**Called by dev10x:gh-pr-monitor:**
```
dev10x:gh-pr-monitor detects new comments →
  delegate to dev10x:gh-pr-respond with PR URL (batch mode)
```

## References

### references/github_api.md

Contains GitHub API documentation for:
- Listing PR comments
- Fetching single comments
- Creating replies
- Resolving review threads (GraphQL)
- Filtering and querying
