---
name: dx:defer
description: >
  Use when a task should be saved for later — so deferred items land
  where they will actually be rediscovered (PR, ticket, code, Slack,
  or project TODO) instead of being forgotten.
user-invocable: true
invocation-name: dx:defer
---

# dx:defer — Smart Deferral Router

**Announce:** "Using dx:defer to save this item for later."

## Overview

Route a single deferred item to the right discovery context. Can be
invoked standalone or called by `dx:wrap-up` for each open loop.

## Workflow

### 1. Receive item

Accept the item to defer. This is either:
- Passed from `dx:wrap-up` (structured)
- Provided by user directly: `/dx:defer "item description"`

### 2. Detect context

Run these checks to determine available targets:

**Branch + ticket:**
```bash
git branch --show-current
```
Extract ticket ID from branch name (pattern: `username/TICKET-ID/desc`).

**Open PR:**
```bash
gh pr list --head "$(git branch --show-current)" --state open \
  --json number,url --limit 1
```

**Repository root:**
```bash
basename "$(git rev-parse --show-toplevel)"
```

### 3. Present targets

Build target list based on detected context. Always available:

| # | Target | When it surfaces |
|---|--------|-----------------|
| 1 | `.claude/TODO.md` | Next Claude session in this project |
| 2 | Slack DM to self | When clearing Slack messages |
| 3 | Create issue | When triaging backlog or planning sprint |

Conditionally available (include only when detected):

| # | Target | Condition |
|---|--------|-----------|
| 4 | Issue tracker comment | Ticket ID found in branch |
| 5 | PR comment | Open PR found for current branch |
| 5b | PR session bookmark | Open PR + session end / wrap-up context |
| 6 | Inline TODO/FIXME | User mentions a specific file |
| 7 | Keep in session | User wants to finish later this session |

Present using `AskUserQuestion` with multiSelect enabled so user
can pick multiple targets for the same item.

### 4. Delegate to targets

For each selected target:

| Target | Action |
|--------|--------|
| `.claude/TODO.md` | Invoke `dx:todo` (project file mode) |
| Slack DM | Invoke `dx:remind` |
| Create issue | Ask user which tracker (Linear, GitHub Issues, Jira, etc.) then create the issue with the deferred item as description |
| Issue tracker comment | Post comment via the appropriate tracker MCP or CLI tool |
| PR comment | Post as PR comment (simple format) |
| PR session bookmark | Post as PR comment with rich metadata (see PR Bookmark Format below) |
| Inline TODO/FIXME | Invoke `dx:todo` (inline mode) — ask user for file path if not provided |
| Keep in session | Invoke `dx:tasks` to create a TaskCreate entry |

### 5. Confirm

Report which targets received the item:

```
Deferred "Add order confirmation email":
  ✓ .claude/TODO.md (project)
  ✓ Slack DM sent
```

## Formatting for External Targets

**Issue tracker comment:**
```markdown
🔖 **Deferred from session [YYYY-MM-DD]**

<item description>

_Branch: `<branch-name>`_
```

**PR comment (simple):**
```markdown
🔖 **Deferred item**

<item description>

_Session: YYYY-MM-DD_
```

**PR session bookmark (rich metadata):**

Use this format when deferring work on a PR to the next session. It
provides enough context for `claude --resume` to pick up where the
session left off.

Gather this data before composing:

1. **Session ID** — extract from the current JSONL filename:
   ```bash
   basename "$(ls -t ~/.claude/projects/<encoded-cwd>/*.jsonl | head -1)" .jsonl
   ```
2. **Review threads** — list root comments and their status:
   ```bash
   ~/.claude/tools/gh-pr-comments.py list \
     --pr {number} --root-only
   ```
3. **Unaddressed comments** — check if any remain:
   ```bash
   ~/.claude/tools/gh-pr-comments.py list \
     --pr {number} --root-only --unaddressed {username}
   ```
4. **Current commit** — `git log --oneline <base-branch>..HEAD`
5. **PR body context** — `gh pr view {number} --json body -q '.body'`

Compose the comment:

```markdown
> **Automated reminder** — @{reviewer} session bookmark for
> picking up this review tomorrow.
> Session ID: `{session_id}`
> Resume with: `claude --resume {session_id}`

---

## PR #{number} Review — State of Play ({date})

### Context

{1-2 sentence summary of what the PR does}

### Review comments addressed

| Thread | Status | Key point |
|--------|--------|-----------|
| [r{id}]({url}) | Addressed / Open | {one-line summary} |

### Current state after grooming (`{short_sha}`)

{Brief description of production code and test state}

### What to do next

1. {next step}
2. {next step}
```

Write the comment to a temp file and post via `--body-file`:
```bash
gh pr comment {number} --body-file /tmp/claude/pr-comment-{number}.txt
```

To **update** an existing bookmark comment instead of creating a new one:
```bash
gh api repos/{owner}/{repo}/issues/comments/{comment_id} \
  -X PATCH -F body=@/tmp/claude/pr-comment-{number}.txt
```

## Used By

- `dx:wrap-up` — Phase 3 calls this for each deferred item
- `pr:bookmark` — thin wrapper that pre-selects PR session bookmark target
