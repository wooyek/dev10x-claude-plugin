---
name: dev10x:work-on
description: >
  Start work on any input — ticket URL, PR link, Slack thread,
  Sentry issue, or free text. Classifies inputs, gathers context
  in parallel, builds a supervisor-approved task list, and executes
  adaptively with pause/resume support.
user-invocable: true
invocation-name: dev10x:work-on
allowed-tools:
  - Bash(~/.claude/skills/gh/scripts/*:*)
  - Bash(~/.claude/skills/jira/scripts/*:*)
  - Write(~/.claude/projects/**/**)
---

# dev10x:work-on — Adaptive Work Orchestrator

## Overview

This skill turns any combination of inputs into a structured,
supervisor-approved work plan. It runs in four phases:

1. **Parse & Classify** — identify what each input is
2. **Gather** — fetch context from all sources in parallel
3. **Plan** — build a task list for supervisor approval
4. **Execute** — work through tasks, expanding epics on demand

The supervisor sees progress via `TaskList`, can approve/edit
the plan, and can pause at any point with `dev10x:wrap-up`.

**Rule: ALWAYS use `TaskCreate`** — even for single-task work.
The visible task list is the supervisor's interface for adding
new tasks mid-session. Skipping it removes that capability.

**Phase-level tasks upfront:** At session start, create exactly
4 top-level tasks — one per phase:

```
TaskCreate(subject="Phase 1: Parse & Classify inputs",
    activeForm="Classifying inputs")
TaskCreate(subject="Phase 2: Gather context",
    activeForm="Gathering context")
TaskCreate(subject="Phase 3: Build work plan",
    activeForm="Building plan")
TaskCreate(subject="Phase 4: Execute plan",
    activeForm="Executing")
```

Set sequential dependencies (each phase blocked by the previous).
During each phase, create subtasks for the concrete work items
discovered — e.g., Phase 2 creates one subtask per source being
fetched, Phase 4 creates subtasks per plan step.

## Prerequisites

| Capability | Required for | Tool |
|------------|-------------|------|
| GitHub CLI | GitHub issues, PRs | `gh` CLI |
| Linear MCP | Linear tickets | `mcp__claude_ai_Linear__*` |
| JIRA | JIRA tickets | `dev10x:jira` plugin + `JIRA_TENANT` env var + keyring |
| Sentry MCP | Sentry issues | `mcp__sentry__*` |
| Slack MCP | Slack threads | `mcp__claude_ai_Slack__*` |

Not all are required — only those matching the input types.

## When to Use

- User provides any combination of: ticket URL/ID, PR link, Slack
  thread, Sentry link, or free text description
- User wants to start structured work with progress tracking
- User wants comprehensive context before starting

---

## Phase 1: Parse & Classify

Accept the user's arguments as a space-separated list. Each
argument is classified independently:

| Pattern | Type | Action |
|---------|------|--------|
| `https://github.com/.../issues/N` | `github-issue` | Extract repo + issue number |
| `https://github.com/.../pull/N` | `github-pr` | Extract repo + PR number |
| `https://linear.app/.../issue/XXX-N/...` | `linear-ticket` | Extract ticket ID (e.g., `TEAM-133`) |
| `https://.*slack.com/archives/C.../p...` | `slack-thread` | Store channel + timestamp |
| `https://sentry.io/.../issues/N` | `sentry-issue` | Extract issue ID |
| `https://*.sentry.io/issues/N` | `sentry-issue` | Extract issue ID |
| `https://...atlassian.net/browse/XX-N` | `jira-ticket` | Extract ticket ID |
| `GH-N` | `github-issue` | Route to `detect-tracker.sh` |
| `TEAM-N` (Linear prefix) | `linear-ticket` | Route to `detect-tracker.sh` |
| `TT-N` | `jira-ticket` | Route to `detect-tracker.sh` |
| `#N` (bare number) | `github-pr` | Resolve against current repo |
| Anything else | `note` | Store as free-text context |

For ticket IDs, run the tracker detector (from `dev10x:gh` skill):
```bash
~/.claude/skills/gh/scripts/detect-tracker.sh "$TICKET_ID"
```
Parse `TRACKER`, `TICKET_NUMBER`, and `FIXES_URL` from output.

Each classified input becomes a **source** entry with its type and
extracted identifiers. Collect all sources into a list for Phase 2.

### Early Workspace Decision

After classification, determine whether a branch is needed and
what workspace state we're in. This decision happens early because
it affects Phase 3 planning.

**Decision matrix:**

| Work type | Branch required? | Why |
|-----------|-----------------|-----|
| Ticket (feature/bugfix) | Yes | PR is the goal |
| PR continuation | No | Branch already exists |
| Local-only (free text) | Deferred | Decided in Phase 4 |
| Investigation only | No | No code changes expected |

**Detect current workspace state:**

```bash
# Is CWD a worktree?
if [ -f .git ]; then
  WORKSPACE="worktree"
  WT_BRANCH=$(git symbolic-ref --short HEAD)
else
  WORKSPACE="main-repo"
fi
```

**Worktree branch check:** If the CWD is a worktree and the
current branch is a generic worktree branch (e.g., `wt/<name>`
or matches the worktree directory name but has no ticket ID),
flag it for replacement. A work-specific branch must be created
before any commits:

| Workspace state | Branch pattern | Action |
|----------------|---------------|--------|
| Main repo, on develop | Any ticket | Create branch (Phase 4.1) |
| Main repo, on feature branch | Matching ticket | Reuse branch |
| Worktree, generic WT branch | Any ticket | Create work-specific branch (Phase 4.1) |
| Worktree, matching feature branch | Same ticket | Reuse branch |

Store the workspace decision in the Phase 1 output so Phase 3
can include or skip the workspace setup subtask.

---

## Phase 2: Gather (Quick & Parallel via Subagents)

Fetch context from all sources in parallel using subagents.
Each subagent receives only its source identifiers and returns
a structured summary — keeping the main session lean.

See `references/task-orchestration.md` Pattern 4 (Subagent
Dispatch) for the full pattern.

### Subtask Creation

Before dispatching, create one subtask per source under the
Phase 2 parent task:

```
TaskCreate(subject="Fetch linear-ticket DEV-42",
    parentTaskId=phase2TaskId)
TaskCreate(subject="Fetch sentry-issue #5201839452",
    parentTaskId=phase2TaskId)
TaskCreate(subject="Fetch slack-thread #channel",
    parentTaskId=phase2TaskId)
```

Mark each subtask `completed` as its subagent returns.
After cross-reference expansion, create additional subtasks
for newly discovered sources.

### Subagent Dispatch

Dispatch one Explore subagent per source in a single tool-call
block. Each returns a structured summary, not raw API output:

```
# Single tool-call block — all launch concurrently
Agent(subagent_type="Explore",
    description=f"Fetch {source.type} {source.id}",
    prompt=f"""Fetch context for {source.type}: {source.id}
    {source_specific_instructions}
    Return a structured summary:
    - Title/subject
    - Status (open/closed/merged)
    - Key details (2-3 sentences)
    - Cross-references found (URLs, ticket IDs)
    Do NOT return full body text — summarize.""",
    run_in_background=true)
```

### Source-Specific Instructions

| Source type | Subagent instructions |
|-------------|----------------------|
| `github-issue` | Run `gh-issue-get.sh "$NUMBER" "$REPO"`. Return title, status, labels, body summary, linked PRs. |
| `github-pr` | Run `gh pr view --json title,body,headRefName,state,mergedAt,reviews`. Return title, status, branch, review comment count. |
| `linear-ticket` | Call `mcp__claude_ai_Linear__get_issue(issueId)`. Return title, status, parent ID, relations, comment summaries. |
| `jira-ticket` | Run `jira-get.sh "$ID"`. Return title, status, assignee, linked issues. |
| `slack-thread` | Call `mcp__claude_ai_Slack__slack_read_thread(channelId, threadTs)`. Return message count, key decisions, action items. |
| `sentry-issue` | Call `mcp__sentry__get_issue_details(issueId)`. Return error type, frequency, first/last seen, top stack frame. |
| `note` | No subagent needed — pass through as-is. |

### Cross-Reference Expansion (One Level)

After the initial fetch, scan all gathered text for references
to other sources. Add them to the sources list and fetch:

- **PR body** mentions `Fixes GH-N` or `Fixes TEAM-N` (with or without colon) → fetch that ticket
- **Ticket body** contains Sentry URL → fetch that Sentry issue
- **Ticket body** mentions PR `#N` or branch name → fetch that PR
- **Linear ticket** has parent or relations → fetch related tickets
- **Ticket comments** contain any of the above patterns → fetch

Do NOT expand beyond one level — keep the gathering phase fast.

### Output: Context Summary

Present a structured summary of everything gathered:

```markdown
## Context Summary

### Sources (N gathered)
- [github-issue] GH-15: Title here (OPEN)
- [slack-thread] #channel-name: 5 messages
- [sentry-issue] #12345: ErrorType — 145 events in 7 days
- [note] "check the retry logic"

### Cross-References Found
- [sentry-issue] #67890 (from ticket body)
- [github-pr] #42: PR title (merged)

### Key Details
[Brief synthesis: what the work is about, who reported it,
severity if applicable, related context from Slack/Sentry]
```

---

## Phase 3: Plan (Lightweight Steps)

Build a **high-level task list** using `TaskCreate`. **This is
mandatory** — always create at least one task, even when the work
seems trivial. The task list is the supervisor's interface for
tracking progress and adding new tasks during the session.

The plan is adapted based on what was gathered — not a fixed
template.

### Step Types

- **Detailed** — small, immediately executable (2-5 min).
  Created with `metadata: {"type": "detailed"}`.
- **Epic** — placeholder for a phase expanded when reached.
  Created with `metadata: {"type": "epic"}`. Description says
  what the phase accomplishes, not how.

### Generating the Plan

Examine the gathered context and construct a task list. Use these
heuristics to decide which tasks to include:

**Always include (if a ticket was found and branch is needed per
Phase 1 workspace decision):**
- Set up workspace (branch or worktree) — detailed. Skip if
  Phase 1 detected a matching feature branch already exists.
- Draft Job Story — detailed

**Include based on context:**

| Context signal | Tasks to add |
|---------------|-------------|
| Ticket with implementation work | Design approach (epic), Implement (epic), Verify (epic) |
| Sentry issue found | Reproduce issue (detailed), Investigate root cause (epic) |
| PR already exists | Fetch PR context (detailed), Address review comments (epic) |
| Multiple related tickets | Synthesize requirements (detailed) |
| Slack thread with discussion | Summarize key decisions (detailed) |

**Always include at the end:**
- Create PR & ensure CI passes — epic
- Apply fixups to review comments — epic
- Groom commit history — detailed
- Request review — detailed
- Verify acceptance criteria met — detailed (see below)

These plan steps become subtasks of the Phase 4 top-level task.
The last subtask is always acceptance criteria verification.

### Acceptance Criteria Verification

The **last task** in every plan verifies the work is shippable
or ready for handover. Read the acceptance criteria YAML file:

```
~/.claude/projects/<project>/memory/acceptance-criteria.yaml
```

**Determine the work type** from the gathered context:

| Context | Work type |
|---------|-----------|
| Ticket with implementation | `feature` |
| Sentry/bug ticket | `bugfix` |
| PR with review comments | `pr-continuation` |
| No ticket, no PR | `local-only` |
| Sentry/Slack only, no fix planned | `investigation` |

**YAML schema:**

```yaml
# acceptance-criteria.yaml
defaults:
  feature:
    criteria: >
      PR passing CI with automatic fixups applied to review
      comments, groomed commit history, and review request
      published
  bugfix:
    criteria: >
      PR passing CI with automatic fixups applied to review
      comments, regression test covering the fix, groomed
      commit history, and review request published
  pr-continuation:
    criteria: >
      PR passing CI with fixups applied to all unaddressed
      review comments, groomed commit history, and re-review
      requested
  local-only:
    criteria: "Changes verified locally"
  investigation:
    criteria: "Findings documented, next steps clear"
overrides: {}  # populated when user persists a choice
```

**If the file is absent** on first use, use the hardcoded
defaults above — do not fail or skip the verification step.
Create the file only when the user persists a non-default
choice.

**Resolve criteria** in this order:
1. Check `overrides` for a matching `work_type` with
   `persist: false` — use if found, then **remove** the entry
2. Check `overrides` for a matching `work_type` with
   `persist: true` — use if found
3. Fall back to `defaults[work_type].criteria` from the file
4. If the file is absent or the work type has no entry, use
   the hardcoded defaults above

**Present the criteria** when building the plan. Show the
resolved criteria in the final task description. If the user
has persistent overrides from past sessions, present them
as choices alongside the default:

```
Acceptance criteria for this feature work:
- PR is approved, CI passes, ready to merge (Default)
- PR created and CI green, skip review (Your past choice)
- Different criteria this time
```

If the user picks a non-default option, ask whether to
persist it (`AskUserQuestion` with "Always" / "Just this
time"). Update the YAML file accordingly:
- `persist: true` → add to `overrides` for future sessions
- `persist: false` → add with `persist: false`; the skill
  removes consumed one-time overrides after use

### Example Plans

**Feature from ticket** (subtasks of Phase 4):
```
4.1  [detailed] Set up workspace (branch, worktree)
4.2  [detailed] Draft Job Story
4.3  [epic]     Design implementation approach
4.4  [epic]     Implement changes
4.5  [epic]     Verify (tests, lint)
4.6  [epic]     Create PR & ensure CI passes
4.7  [epic]     Apply fixups to review comments
4.8  [detailed] Groom commit history
4.9  [detailed] Request review
4.10 [detailed] Verify acceptance criteria met
```

**Bug fix from Sentry + ticket:**
```
4.1  [detailed] Set up workspace
4.2  [detailed] Reproduce the issue locally
4.3  [epic]     Investigate root cause
4.4  [epic]     Implement fix
4.5  [epic]     Verify fix (tests, regression)
4.6  [epic]     Create PR & ensure CI passes
4.7  [epic]     Apply fixups to review comments
4.8  [detailed] Groom commit history
4.9  [detailed] Request review
4.10 [detailed] Verify acceptance criteria met
```

**PR continuation:**
```
4.1  [detailed] Fetch PR and review context
4.2  [epic]     Address review comments
4.3  [epic]     Apply fixups to unaddressed comments
4.4  [epic]     Verify changes pass CI
4.5  [detailed] Groom commit history
4.6  [detailed] Request re-review
4.7  [detailed] Verify acceptance criteria met
```

**Local-only work (no ticket, no PR):**
```
4.1  [detailed] Summarize the work from gathered context
4.2  [epic]     Implement changes
4.3  [epic]     Verify
4.4  [detailed] Decide: create ticket, create PR, or done
4.5  [epic]     Create PR & ensure CI passes (if decided)
4.6  [epic]     Apply fixups to review comments (if PR)
4.7  [detailed] Groom commit history (if PR)
4.8  [detailed] Request review (if PR)
4.9  [detailed] Verify acceptance criteria met
```

### Supervisor Approval Gate

Present the plan as a numbered list. Then use `AskUserQuestion`:

- **Approve (Recommended)** — start execution
- **Edit** — describe what to change (add/remove/reorder steps)

After approval, set task dependencies where appropriate (use
`TaskUpdate` with `addBlockedBy`). Mark the first task as
`in_progress` and begin Phase 4.

---

## Phase 4: Execute (Adaptive, Auto-Advance)

Work through the approved task list. Update task status via
`TaskUpdate` as work progresses.

### Auto-Advance Rule

See `references/task-orchestration.md` for the full pattern.

**Complete a task → immediately start the next.** Do not pause
between tasks to ask "should I continue?" or wait for the user
to say "go" / "next" / "continue". The approved plan is the
authorization to proceed.

**Batched Decision Queue:** When a task hits a genuine A/B
decision, do NOT interrupt the user immediately. Instead:

1. Queue the decision in task metadata:
   ```
   TaskUpdate(taskId, status="pending",
       metadata={"decision_needed": "description",
                 "options": ["A", "B", "C"]})
   ```
2. Move to the next unblocked task and keep advancing.
3. Only interrupt when ALL tasks are blocked — collect all
   queued decisions into one `AskUserQuestion` batch (1-4 Qs).
4. After the user answers, unblock and resume auto-advancing.

The supervisor can step away, come back to answer all decisions
at once, then step away again confident maximum progress will
happen before the next interruption.

**If blocked on the current task** (waiting for user input,
external dependency, CI), check whether the next unblocked
task can start. Examples:
- Waiting for CI? Start self-review in parallel.
- Waiting for user input on approach? Create the branch or
  draft the Job Story meanwhile.
- Stuck on a sub-task? Mark it `pending` with a note and
  advance to the next unblocked task in the list.

Return to the blocked task once the blocker resolves.

### Executing Detailed Tasks

Run the task directly. Common detailed tasks delegate to skills:

| Task | Delegated to |
|------|-------------|
| Set up workspace (branch) | `dev10x:ticket-branch` skill |
| Set up workspace (worktree) | `dev10x:git-worktree` skill |
| Draft Job Story | `dev10x:jtbd` skill (attended mode) |
| Update ticket status | Linear MCP (see references/team-info.md) |
| Fetch PR context | `gh pr view` + `gh pr diff` |
| Create PR | `dev10x:gh-pr-create` skill |
| Monitor CI | `dev10x:gh-pr-monitor` skill |
| Apply fixups to review | `dev10x:gh-pr-respond` skill |
| Groom commit history | `dev10x:git-groom` skill |
| Request review | `dev10x:gh-pr-request-review` skill |

After completing a detailed task, mark it `completed` via
`TaskUpdate` and move to the next task.

### Expanding Epic Tasks

When reaching an epic task:

1. **Read the epic description** and the gathered context
2. **Generate sub-tasks** — break the epic into detailed steps.
   This may involve:
   - Reading code to understand scope
   - `AskUserQuestion` for A/B decisions (e.g., "approach X
     vs approach Y?") — but only when the choice genuinely
     cannot be inferred from context
   - Follow-up information gathering
3. **Present sub-tasks** briefly (inline, not a new approval
   gate) and begin executing immediately. Only ask for
   approval if the expansion reveals unexpected scope or
   trade-offs the supervisor should weigh in on.
4. **Check for parallelism** — if sub-tasks are independent,
   ask the supervisor before launching parallel agents
5. **Execute sub-tasks**, marking each completed as they finish.
   Auto-advance between sub-tasks (same rule as top-level).
6. **Mark the epic completed** when all sub-tasks are done

### Parallelism Policy

| Phase | Parallelism | Approval needed? |
|-------|------------|-----------------|
| Phase 2 (Gather) | Auto-parallel | No |
| Phase 4 (detailed tasks) | Sequential | No |
| Phase 4 (epic sub-tasks) | Parallel if independent | Yes — ask supervisor |

When asking about parallelism, present which tasks would run
concurrently and why they're independent:

```
Tasks 4a and 4b are independent (different files, no shared state).
Run them in parallel?
- Yes, launch parallel agents (Recommended)
- No, run sequentially
```

### Skill Delegation During Execution

**Workspace setup** (uses the decision from Phase 1):

| State | Action |
|-------|--------|
| Main repo, user wants worktree | Invoke `dev10x:git-worktree` (creates branch internally — do NOT call `dev10x:ticket-branch` first) |
| Main repo, work here | Invoke `dev10x:ticket-branch` to create feature branch |
| Worktree, generic WT branch | Invoke `dev10x:ticket-branch` to create work-specific branch from within the worktree |
| Worktree, matching feature branch | No action needed — branch already exists |

If the Phase 1 workspace decision was deferred (local-only
work), ask at the start of Phase 4:
```
AskUserQuestion(questions=[{
    question: "Where should we work?",
    header: "Workspace",
    options: [
        {label: "Work here (Recommended)",
         description: "Use current directory and branch"},
        {label: "New worktree",
         description: "Create an isolated worktree"}
    ],
    multiSelect: false
}])
```

**Job Story drafting:**
- MUST invoke `Skill(dev10x:jtbd)` explicitly — never draft inline
- Pass gathered context to avoid redundant API calls
- If approved, write back to the ticket:

| Tracker | Write-back |
|---------|-----------|
| GitHub | `gh issue comment` |
| Linear | Prepend to description via `save_issue` |
| JIRA | `jira-update.sh` |

**Ticket status update (Linear only):**
1. Get statuses: `list_issue_statuses(teamId)` from
   references/team-info.md
2. Find "In Progress" (type `started`)
3. Update: `save_issue(id, stateId)`
4. Skip if already "In Progress"; warn if "Done"/"Canceled"

---

## Pause/Resume

At any pause signal ("wrap up", "pause", "that's enough for
today", end-of-session):

1. Invoke `dev10x:wrap-up` — it reads `TaskList` and discovers all
   open tasks automatically
2. `dev10x:wrap-up` handles routing each open item (PR bookmark,
   TODO.md, Slack DM, etc.)
3. The task list itself serves as resume context — when the user
   resumes work, they can invoke `dev10x:discover` to find deferred
   items and `dev10x:tasks` to see the saved task list

No custom bookmarking needed — leverage existing `dev10x:wrap-up`
and `dev10x:defer` infrastructure.

---

## Important Notes

- **Always create tasks via `TaskCreate`** — never skip the task
  list, even for single-step work. The supervisor uses it to add
  new tasks mid-session.
- Always verify ticket exists before creating a branch
- If ticket is "Done"/"Canceled" (Linear) or "closed" (GitHub),
  warn the user before proceeding
- Handle errors gracefully — if a fetch fails, continue with
  what was gathered and note the failure in the context summary
- Linear team UUID is in `references/team-info.md` (template)
- After completing work, use `dev10x:gh-pr-create` to create the PR
- Do not modify ticket description or add comments unless the
  user explicitly approves (e.g., Job Story write-back)

## Resources

### references/team-info.md

Linear team configuration template: UUID, status mappings,
branch naming, Sentry integration patterns.

---

## Examples

### Example 1: Single Ticket URL

**User:** `/dev10x:work-on https://github.com/org/repo/issues/15`

**Phase 1:** Classify → `github-issue`, repo=`org/repo`, number=15

**Phase 2:** Fetch issue. Body mentions Sentry URL → fetch Sentry
issue. Body mentions PR #42 → fetch PR. Produce context summary.

**Phase 3:** Build plan (subtasks of Phase 4):
```
4.1  [detailed] Set up workspace
4.2  [detailed] Draft Job Story
4.3  [epic]     Design implementation approach
4.4  [epic]     Implement changes
4.5  [epic]     Verify
4.6  [epic]     Create PR & ensure CI passes
4.7  [epic]     Apply fixups to review comments
4.8  [detailed] Groom commit history
4.9  [detailed] Request review
4.10 [detailed] Verify acceptance criteria met
```
Supervisor approves.

**Phase 4:** Auto-advance through subtasks 4.1-4.10, expanding
epics as reached. No pauses between tasks unless a genuine
decision is needed.

### Example 2: Multiple Inputs

**User:** `/dev10x:work-on TEAM-133 https://slack.com/archives/C123/p456 "check the retry logic"`

**Phase 1:** Classify →
- `linear-ticket` TEAM-133
- `slack-thread` C123/p456
- `note` "check the retry logic"

**Phase 2:** Fetch all three in parallel. Linear ticket links to
Sentry issue → fetch that too. Produce context summary with 4
sources.

**Phase 3:** Build plan (adapted — Sentry issue means
"Reproduce" task added):
```
4.1  [detailed] Set up workspace
4.2  [detailed] Reproduce the Sentry error locally
4.3  [detailed] Draft Job Story
4.4  [epic]     Investigate root cause
4.5  [epic]     Implement fix
4.6  [epic]     Verify fix
4.7  [epic]     Create PR & ensure CI passes
4.8  [epic]     Apply fixups to review comments
4.9  [detailed] Groom commit history
4.10 [detailed] Request review
4.11 [detailed] Verify acceptance criteria met
```

### Example 3: PR Continuation

**User:** `/dev10x:work-on https://github.com/org/repo/pull/42`

**Phase 1:** Classify → `github-pr`, number=42

**Phase 2:** Fetch PR. Body has `Fixes GH-15` → fetch issue.
PR has 3 review comments → note them.

**Phase 3:** Build plan:
```
4.1  [detailed] Fetch review comments and understand feedback
4.2  [epic]     Address review comments
4.3  [epic]     Apply fixups to unaddressed comments
4.4  [epic]     Verify CI passes
4.5  [detailed] Groom commit history
4.6  [detailed] Request re-review
4.7  [detailed] Verify acceptance criteria met
```

### Example 4: Mid-Workflow Pause

User is at task 4 of 7 and says "let's wrap up for today".

1. Skill detects pause signal
2. Invokes `dev10x:wrap-up`
3. `dev10x:wrap-up` reads `TaskList` — sees 3 pending tasks
4. Routes each via `dev10x:defer` (e.g., PR bookmark, TODO.md)
5. Session ends with bookmark saved

Next session: user runs `dev10x:discover` to find bookmarks and
resume where they left off.
