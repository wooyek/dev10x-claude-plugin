---
name: dev10x:project-scope
description: Scope a multi-ticket project with milestones, blocking relationships, and tracker integration. Accepts a parent ticket URL/ID or free-text description and creates the full project structure in Linear or JIRA.
user-invocable: true
invocation-name: dev10x:project-scope
allowed-tools:
  - mcp__claude_ai_Linear__get_issue
  - mcp__claude_ai_Linear__save_issue
  - mcp__claude_ai_Linear__save_project
  - mcp__claude_ai_Linear__get_project
  - mcp__claude_ai_Linear__save_milestone
  - mcp__claude_ai_Linear__list_milestones
  - mcp__claude_ai_Linear__list_issue_statuses
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/gh-context/scripts/*:*)
---

# Project Scope - Multi-Ticket Project Creation

## Overview

This skill orchestrates multi-ticket project creation with milestones
and blocking relationships. It takes a parent ticket or free-text
description and produces a complete project structure in the tracker.

**Use when:**
- Scoping a feature that spans multiple tickets and milestones
- Breaking down an epic or ADR into implementation phases
- Creating a project with blocking chains between tickets

**Do NOT use for:**
- Single-ticket scoping (use `dev10x:ticket-scope`)
- Architectural decisions without implementation tickets (use `dev10x:adr`)
- Creating a single ticket (use `dev10x:ticket-create`)

## Orchestration

This skill follows `references/task-orchestration.md` patterns
(Tier: Standard).

**Auto-advance:** Complete each phase and immediately start the next.
Never pause between phases to ask "should I continue?".

**REQUIRED: Create tasks before ANY work.** Execute these
`TaskCreate` calls at startup:

1. `TaskCreate(subject="Gather & understand input", activeForm="Gathering context")`
2. `TaskCreate(subject="Scope project structure", activeForm="Scoping project")`
3. `TaskCreate(subject="Create tracker structure", activeForm="Creating structure")`
4. `TaskCreate(subject="Verify & report results", activeForm="Verifying entities")`

Set sequential dependencies: scope blocked by gather, create blocked
by scope, verify blocked by create.

## Input Classification

| Input | Type | Behavior |
|-------|------|----------|
| `PAY-662` or `TT-123` | Ticket ID | Run `detect-tracker.sh`, fetch as parent |
| `https://linear.app/.../issue/XXX-N/...` | Linear URL | Extract ID, fetch as parent |
| `https://*.atlassian.net/browse/XX-N` | JIRA URL | Extract ID, fetch as parent |
| `https://github.com/.../issues/N` | GitHub URL | Extract repo + number, fetch as parent |
| Free text description | New project | Create parent ticket first |

## Phase 1: Gather & Understand

### 1.1 Classify Input

Determine whether the user provided a ticket reference or free text.

### 1.2 Fetch Context

**If ticket reference:** Fetch ticket details (title, description,
comments, labels, related tickets) via Linear MCP or GitHub CLI.

**If free text:** Store as project description for Phase 2.

### 1.3 Detect Tracker

Run `${CLAUDE_PLUGIN_ROOT}/skills/gh-context/scripts/detect-tracker.sh`
to determine the project's tracker backend.

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text) when
tracker cannot be detected automatically (e.g., free-text input
with no branch context):

```
AskUserQuestion(questions=[{
    question: "Which tracker should we use for this project?",
    header: "Tracker",
    options: [
        {label: "Linear (Recommended)",
         description: "Create Linear project with milestones"},
        {label: "JIRA",
         description: "Create JIRA epic with sub-tasks"}
    ],
    multiSelect: false
}])
```

### 1.4 Research Codebase

If the project involves code changes, explore the codebase for
relevant patterns, existing components, and architectural context.

## Phase 2: High-Level Scope

### 2.1 Produce Scope Document

Generate the following sections:

1. **Executive summary** — 1-2 paragraphs describing the project goal
   and approach
2. **Milestones** — named phases with goals and ordering
3. **Tickets per milestone** — title, 1-2 sentence description,
   priority, estimated complexity
4. **Blocking chain** — which tickets block which and why

Tickets are intentionally high-level. Further refinement via
`dev10x:ticket-scope` is expected for individual tickets.

### 2.2 Present for Approval

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
This blocks execution until the user responds:

```
AskUserQuestion(questions=[{
    question: "Approve this project structure?",
    header: "Scope Review",
    options: [
        {label: "Approve (Recommended)",
         description: "Create milestones and tickets as shown"},
        {label: "Revise",
         description: "I have corrections to the structure"},
        {label: "More research needed",
         description: "Need to explore additional areas"}
    ],
    multiSelect: false
}])
```

If "Revise": incorporate feedback and re-present.
If "More research": return to Phase 1.4 with user guidance.

## Phase 3: Create Structure

### 3.1 Tracker Dispatch

| Operation | Linear | JIRA |
|-----------|--------|------|
| Create project | `save_project` (optional) | Epic via `dev10x:jira` |
| Create milestone | `save_milestone` | Sprint/Fix Version via `dev10x:jira` |
| Create ticket | `save_issue` + milestone + project | via `dev10x:jira` |
| Set blocking | `save_issue` blockedBy/blocks | Link via `dev10x:jira` |

### 3.2 Create/Resolve Parent Ticket

**If free text:** Invoke `Skill(skill="dev10x:ticket-create")` to
create the parent ticket using the executive summary as description.

**If ticket reference:** Use the fetched ticket as parent.

### 3.3 Create Project Entity (Optional)

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
This blocks execution until the user responds:

```
AskUserQuestion(questions=[{
    question: "Create a project-level entity in the tracker?",
    header: "Project",
    options: [
        {label: "Create project entity (Recommended)",
         description: "Enables roadmap views and project tracking"},
        {label: "Skip",
         description: "Just milestones and tickets, no project entity"}
    ],
    multiSelect: false
}])
```

### 3.4 Create Milestones

Create milestones sequentially (tickets reference them by ID).
Check for existing milestones by name before creating to avoid
duplicates.

### 3.5 Create Tickets

Create all tickets with milestone and project assignments.
Batch creation is possible since all milestones exist at this point.
Check for existing tickets by title before creating.

### 3.6 Set Blocking Relationships

Set blocking/blocked-by relationships between tickets per the
approved blocking chain. Execute in parallel since all tickets exist.

### 3.7 Link Tickets to Project

Link all tickets to the project entity (if created in 3.3).
Execute in parallel.

## Phase 4: Verify & Report

### 4.1 Re-Fetch Entities

Re-fetch all created entities to verify:
- Milestones are assigned correctly
- Blocking chains are intact
- Project links are set

### 4.2 Structured Summary

Present a summary with:
- Parent ticket link
- Project entity link (if created)
- Milestone list with ticket counts
- Blocking chain visualization
- Links to all created tickets

### 4.3 Failure Reporting

Report any failures with:
- Which entity failed and why
- What succeeded (no rollback)
- Suggested manual remediation steps

## Error Handling

| Scenario | Behavior |
|----------|----------|
| API failure | Retry once, then report with failed entity details |
| Partial creation | Report what succeeded, do not roll back |
| Duplicate detected | Skip creation, use existing entity, log warning |
| Relationship failure | Log and continue with remaining relationships |

## Integration with Other Skills

| Trigger | Skill | Direction |
|---------|-------|-----------|
| Free-text needs parent ticket | `dev10x:ticket-create` | Delegates to |
| Parent needs Job Story | `dev10x:jtbd` | Delegates to (optional) |
| User refines a child ticket | `dev10x:ticket-scope` | User invokes manually |
| User starts work on a ticket | `dev10x:work-on` | User invokes manually |

Child tickets are NOT auto-scoped via `dev10x:ticket-scope`.
High-level fidelity is intentional.
