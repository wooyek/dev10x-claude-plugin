---
name: dx:gh-pr-bookmark
description: >
  Post a rich session bookmark comment on a PR — captures session ID,
  review thread status, current state, and next steps so the next
  session can pick up where this one left off.
user-invocable: true
invocation-name: dx:gh-pr-bookmark
---

# dx:gh-pr-bookmark — PR Session Bookmark

**Announce:** "Using dx:gh-pr-bookmark to save session state to the PR."

## Overview

Thin wrapper around `dx:park` that pre-selects the **PR session
bookmark** target. Use at end-of-session or when pausing work on a PR.

## Workflow

### 1. Detect PR

```bash
gh pr list --head "$(git branch --show-current)" --state open --json number,url --limit 1
```

If no open PR found, tell the user and stop.

### 2. Delegate to dx:park

Invoke `dx:park` with:
- **Item**: the user's description (or "Continuing PR review" if none)
- **Pre-selected target**: `PR session bookmark`

Skip the target selection prompt — this skill always routes to the
PR session bookmark target in `dx:park`.

### 3. Done

`dx:park` handles data gathering, composition, posting, and
confirmation.

## Usage

```
/dx:gh-pr-bookmark                          # bookmark current PR
/dx:gh-pr-bookmark Wait for CI then merge   # bookmark with custom note
```

## See Also

- `dx:park` — full deferral router with all targets
- `dx:wrap-up` — end-of-session orchestrator that may call this
