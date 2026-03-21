---
name: Dev10x:gh-pr-respond
description: >
  Validate and respond to PR review comments. Handles single comment
  (with follow-up offer) or batch mode for all unaddressed comments on
  a PR/review. Orchestrates Dev10x:gh-pr-triage and Dev10x:gh-pr-fixup.
  TRIGGER when: PR has review comments that need responses or fixes.
  DO NOT TRIGGER when: no review comments exist, or user wants to
  create a new PR (use Dev10x:gh-pr-create).
user-invocable: true
invocation-name: Dev10x:gh-pr-respond
allowed-tools:
  - AskUserQuestion
  - Bash(gh:*)
  - Skill(Dev10x:gh-pr-triage)
  - Skill(Dev10x:gh-pr-fixup)
  - Skill(Dev10x:git-groom)
  - Skill(Dev10x:gh-pr-monitor)
  - Skill(Dev10x:git)
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
2. `TaskCreate(subject="Hide obsolete comment", activeForm="Hiding comment")`
3. `TaskCreate(subject="Check remaining comments", activeForm="Checking remaining")`

**Mode B (batch):**
1. `TaskCreate(subject="Collect unaddressed comments", activeForm="Collecting comments")`
2. `TaskCreate(subject=f"Triage {N} comments", activeForm="Triaging comments")`
3. `TaskCreate(subject="Get user approval", activeForm="Awaiting approval")`
4. `TaskCreate(subject="Execute approved responses", activeForm="Executing responses")`
5. `TaskCreate(subject="Resolve threads", activeForm="Resolving threads")`
6. `TaskCreate(subject="Hide obsolete comments", activeForm="Hiding comments")`
7. `TaskCreate(subject="Summary", activeForm="Summarizing")`

Set dependencies and update status as each completes.

**Parallel triage (Mode B Step 2):** Dispatch up to 4 triage
subagents concurrently to reduce processing time. Each subagent
receives only its comment context and returns verdict + draft
reply.

**Batched decisions:** Thread resolution decisions are queued
and presented as a batch after all responses are posted.

## Playbook

This skill is playbook-powered. The workflow steps are defined in
`references/playbook.yaml` with two plays: `single` (Mode A) and
`batch` (Mode B).

**Loading order:**
1. User overrides: `~/.claude/projects/<project>/memory/playbooks/gh-pr-respond.yaml`
2. Defaults: `${CLAUDE_PLUGIN_ROOT}/skills/gh-pr-respond/references/playbook.yaml`

Customize with `/Dev10x:playbook edit gh-pr-respond <play>`.

## Decision Gates

This skill has 6 **blocking decision gates** where execution
MUST pause for user input via the `AskUserQuestion` tool.

**Plain text questions are NOT acceptable** — they don't block
execution, don't provide clickable options, and break the
structured decision flow the user relies on.

Gates numbered by insertion order; execution order differs by mode.

| # | Location | Purpose |
|---|----------|---------|
| 1 | Mode A, Step 1b | Confirm thread resolution |
| 2 | Mode A, Step 3 | Continue / batch / stop |
| 3 | Mode B, Step 3 | Approve / review / skip batch |
| 4 | Mode B, Step 5 | Resolve threads confirmation |
| 5 | Post-Response Continuation | Groom + push + monitor / Push only / Stop |
| 6 | Mode B, Step 5b / Mode A, Step 1c | Hide obsolete comments |

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
- **`Dev10x:gh-pr-triage`** — Validate the comment against the codebase
- **`Dev10x:gh-pr-fixup`** — Implement the fix if the comment is valid

```
Dev10x:gh-pr-respond (this skill)
    ├── Dev10x:gh-pr-triage         → validate, reply if invalid (never auto-resolves)
    ├── resolve gate      → ask user to confirm thread resolution
    └── Dev10x:gh-pr-fixup  → implement fix, fixup commit, reply with ref
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
- Example: `/Dev10x:gh-pr-respond https://...#discussion_r456 Note that PR #1135 is merged`

---

## Mode A: Single Comment

**Trigger:** Input contains `#discussion_r{comment_id}`

### Step 1: Process the comment

Delegate to `Dev10x:gh-pr-triage` with the comment URL (and any additional context).

`Dev10x:gh-pr-triage` returns a verdict: `VALID`, `INVALID`, `QUESTION`, or `OUT_OF_SCOPE`.

- If **VALID** → delegate to `Dev10x:gh-pr-fixup` to implement fix, commit, push,
  and reply.
- If **not VALID** → `Dev10x:gh-pr-triage` has posted a reply but has NOT resolved the
  thread. Ask the user whether to resolve it (see Step 1b).

### Step 1b: Confirm thread resolution (non-VALID only)

When `Dev10x:gh-pr-triage` returns INVALID, QUESTION, or OUT_OF_SCOPE, present the
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

### Step 1c: Hide obsolete comment (optional)

If the thread was resolved in Step 1b, offer to minimize the root
comment to reduce PR conversation noise:

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
Options:
- **"Hide"** — Minimize the comment via GraphQL `minimizeComment`
  with classifier `OUTDATED`
- **"Skip"** — Leave the comment visible

**Skip this gate** if the thread was left open in Step 1b.

When hiding, use the comment's `node_id` (not numeric `id`).
Write the GraphQL mutation to a temp file and reference it with
`-F query=@file` to avoid shell quoting issues with `$` variables:
```bash
# Write mutation to temp file (use mcp__plugin_Dev10x_cli__mktmp)
# Then invoke:
gh api graphql -F query=@/tmp/claude/gh/minimize.graphql \
  -f id='{node_id}' -f classifier='OUTDATED'
```

See `references/github_api.md` § Hiding (Minimizing) Comments.

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

If no unaddressed inline comments found, check for a **body-only
review** (review body text without inline comments). CI hygiene
reviews from `claude[bot]` commonly produce these. If a review
body exists:
1. Extract the review body via
   `gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews`
   filtered by `review_id`
2. Treat the review body as a single top-level comment to address
3. Continue to Step 2 (triage) with this synthetic comment

If neither inline comments nor review body found → report
"No unaddressed comments" and stop.

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

- **VALID** → delegate to `Dev10x:gh-pr-fixup` (one fixup commit per comment)
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

### Step 5b: Hide obsolete comments (optional)

After resolving threads, offer to minimize the resolved comments
to reduce PR conversation noise. This hides comment bodies on
GitHub, showing "This comment was marked as outdated" instead.

**Skip this step** if no threads were resolved in Step 5.

Collect all resolved threads' root comment `node_id` values:

```bash
gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100) {
        nodes {
          isResolved
          comments(first: 1) {
            nodes { id databaseId path body }
          }
        }
      }
    }
  }
}' -f owner='{owner}' -f repo='{repo}' -F pr={pr_number} \
  --jq '[.data.repository.pullRequest.reviewThreads.nodes[]
        | select(.isResolved)
        | .comments.nodes[0]]'
```

Present the resolved comments:

```
{N} resolved thread(s) can be hidden:

1. r{databaseId} on {path}:{line} — "{first_line_of_body}..."
2. r{databaseId} on {path}:{line} — "{first_line_of_body}..."

Hide these comments?
```

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
Options:
- **"Hide all resolved" (Recommended)** — Minimize all resolved
  thread root comments with classifier `OUTDATED`
- **"Review one-by-one"** — Confirm each comment individually
- **"Skip"** — Leave all comments visible

**If "Review one-by-one":** For each comment, present:
```
r{databaseId} on {path}:{line}
  Body: "{body_excerpt}"
  Thread: resolved ✅

Hide this comment?
```
Options: "Hide" / "Skip"

**After confirmation**, minimize approved comments via GraphQL:
```bash
gh api graphql -f query='
mutation($id: ID!, $classifier: ReportedContentClassifiers!) {
  minimizeComment(input: {
    subjectId: $id, classifier: $classifier
  }) {
    minimizedComment { isMinimized minimizedReason }
  }
}' -f id='{node_id}' -f classifier='OUTDATED'
```

See `references/github_api.md` § Hiding (Minimizing) Comments.

### Step 6: Summary

After all comments are processed, report:

```
Batch complete: {N} comments processed
- {x} VALID (fixup commits created)
- {y} INVALID (replied)
- {z} QUESTION (answered)
- {w} OUT_OF_SCOPE (acknowledged)
- {r} threads resolved (user-confirmed)
- {h} comments hidden (minimized)
- {u} threads left open
```

---

## Post-Response Continuation

After all comments are processed (Mode A or Mode B), if fixup commits
were created during this session, offer to continue the full shipping
pipeline:

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
Options:
- **"Full shipping pipeline" (Recommended)** — Execute the complete
  post-response shipping sequence:
  1. `Dev10x:git-groom` — squash fixup commits into clean history
  2. `Dev10x:git` — push with `--force-with-lease`
  3. `gh pr ready` — mark PR ready for review (if still draft)
  4. `Dev10x:gh-pr-monitor` — watch CI and new review comments
  5. If CI passes and no new comments → merge via
     `gh pr merge --squash --delete-branch`
- **"Groom + push only"** — Groom and push, but stop before
  monitoring and merge
- **"Stop"** — End without pushing

This eliminates the manual multi-step chain that was required
after every respond session. The full pipeline handles the entire
groom → push → ready → monitor → merge lifecycle.

**Skip this gate** if no fixup commits were created (e.g., all
comments were INVALID and only replies were posted).

**Solo-maintainer mode:** When the project playbook defines a
solo-maintainer override (no external reviewers), the full
pipeline auto-merges after CI passes without waiting for
external approval.

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
    │       ├── Dev10x:gh-pr-triage → verdict
    │       ├── if VALID → Dev10x:gh-pr-fixup
    │       ├── if not VALID → reply posted, ask user to resolve
    │       ├── if resolved → offer to hide (minimize) comment
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
            ├── hide resolved comments → ask user to confirm hiding
            └── summary
```

## Integration

```
Dev10x:gh-pr-monitor → Dev10x:gh-pr-respond (this skill)
                 ├── Dev10x:gh-pr-triage
                 └── Dev10x:gh-pr-fixup
                      └── commit:fixup
```

**Standalone usage:**
```bash
# Single comment
/Dev10x:gh-pr-respond https://github.com/owner/repo/pull/123#discussion_r456

# Single comment with context
/Dev10x:gh-pr-respond https://github.com/owner/repo/pull/123#discussion_r456 Note that PR #1135 is merged

# Batch — all unaddressed comments on PR
/Dev10x:gh-pr-respond https://github.com/owner/repo/pull/123

# Batch — all comments from a specific review
/Dev10x:gh-pr-respond https://github.com/owner/repo/pull/123#pullrequestreview-789

# Batch — PR number only
/Dev10x:gh-pr-respond 1164
```

**Called by Dev10x:gh-pr-monitor:**
```
Dev10x:gh-pr-monitor detects new comments →
  delegate to Dev10x:gh-pr-respond with PR URL (batch mode)
```

## References

### references/github_api.md

Contains GitHub API documentation for:
- Listing PR comments
- Fetching single comments
- Creating replies
- Resolving review threads (GraphQL)
- Hiding (minimizing) comments (GraphQL)
- Filtering and querying
