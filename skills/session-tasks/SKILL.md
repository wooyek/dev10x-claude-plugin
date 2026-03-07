---
name: dev10x:session-tasks
description: >
  Use when tracking in-session work items — so open loops are visible
  and triageable before session end without losing track of parallel work.
user-invocable: true
invocation-name: dev10x:session-tasks
---

# dev10x:session-tasks — In-Session Task Tracking

**Announce:** "Using dev10x:session-tasks to [show/add/update] session tasks."

## Orchestration

This skill follows `references/task-orchestration.md` patterns.
Create a task at invocation, mark completed when done:

```
TaskCreate(subject="Track session work items",
    activeForm="Tracking items")
# ... do work ...
TaskUpdate(taskId, status="completed")
```

## Overview

Thin wrapper around Claude's `TaskCreate`/`TaskUpdate`/`TaskList` tools
for tracking work items within the current session.

## Commands

### Show tasks

Use `TaskList` to display all current tasks grouped by status.
Present as a markdown table:

| # | Status | Task |
|---|--------|------|
| 1 | in_progress | Implement checkout feature |
| 2 | pending | Create PR for TICKET-42 |
| 3 | completed | Add webhook endpoint |

### Add task

Use `TaskCreate` with:
- `subject`: short task title
- `description`: context, file paths, or links if available

### Update task

Use `TaskUpdate` with the task ID and new `status`:
- `in_progress` — currently working on
- `completed` — done
- `pending` — deferred within this session

## Used By

- `dev10x:park` — when user picks "keep for this session"
- `dev10x:wrap-up` — Phase 1 auto-scan reads the task list
