---
name: dx:tasks
description: >
  Use when tracking in-session work items — so open loops are visible
  and triageable before session end without losing track of parallel work.
user-invocable: true
invocation-name: dx:tasks
---

# dx:tasks — In-Session Task Tracking

**Announce:** "Using dx:tasks to [show/add/update] session tasks."

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

- `dx:defer` — when user picks "keep for this session"
- `dx:wrap-up` — Phase 1 auto-scan reads the task list
