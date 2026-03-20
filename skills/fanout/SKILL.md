---
name: Dev10x:fanout
description: >
  Close multiple open loops in parallel — PRs waiting for review,
  issues ready for implementation, tickets needing attention. Honors
  dependencies, minimizes conflict risk, auto-advances by default.
user-invocable: true
invocation-name: Dev10x:fanout
allowed-tools:
  - AskUserQuestion
  - Skill(skill="Dev10x:work-on")
  - Skill(skill="Dev10x:gh-pr-respond")
  - Skill(skill="Dev10x:gh-pr-monitor")
  - Skill(skill="Dev10x:git-groom")
  - Skill(skill="Dev10x:git-commit")
  - Skill(skill="Dev10x:gh-pr-create")
  - Skill(skill="Dev10x:ticket-branch")
  - Skill(skill="Dev10x:session-wrap-up")
  - mcp__plugin_Dev10x_cli__*
---

# Dev10x:fanout — Parallel Work Stream Orchestrator

**Announce:** "Using Dev10x:fanout to process [N] work items
in parallel."

## Overview

This skill processes multiple independent work items
concurrently, honoring dependency order and minimizing merge
conflict risk. It is the multi-item counterpart to
`Dev10x:work-on` (which handles a single work item).

**When to use fanout vs work-on:**
- **work-on**: Single ticket, PR, or investigation
- **fanout**: Multiple PRs to merge, multiple issues to
  implement, or a mix of both

**Default mode:** Fully autonomous with auto-advancement.
No confirmation gates between items unless a genuine
dependency or conflict is detected.

## Orchestration

This skill follows `references/task-orchestration.md` patterns.

**Auto-advance:** Complete each item, immediately start the
next. Never pause between items to ask "should I continue?"

**REQUIRED: Create tasks before ANY work.** Execute
`TaskCreate` calls at startup — one per phase:

1. `TaskCreate(subject="Scan: discover work items", activeForm="Scanning")`
2. `TaskCreate(subject="Classify: dependency and conflict analysis", activeForm="Classifying")`
3. `TaskCreate(subject="Execute: process work streams", activeForm="Processing")`
4. `TaskCreate(subject="Verify: confirm all items resolved", activeForm="Verifying")`

## Phase 1: Scan

Discover all open work items in the current repo or
specified scope.

**Default scan** (no arguments): Fetch both open PRs and
open issues:
```
gh pr list --state open --json number,title,headRefName,isDraft,mergeable
gh issue list --state open --json number,title,labels
```

**With arguments**: Accept a space-separated list of URLs,
issue numbers, or PR numbers. Classify each per
`Dev10x:work-on` Phase 1 rules.

Create one subtask per discovered item under the Phase 1
parent task.

## Phase 2: Classify

For each work item, determine:

1. **Type**: PR-continuation, feature, bugfix, investigation
2. **Files touched**: Read the PR diff or issue description
   to identify affected files/directories
3. **Dependency edges**: If item A's target files overlap
   with item B's, they conflict — order matters
4. **Priority**: PRs before issues (PRs are closer to done).
   Within PRs: ready-to-merge first, then draft with CI
   passing, then draft needing work.

### Conflict Analysis

Build a conflict graph:

```
For each pair (A, B):
  if files_touched(A) ∩ files_touched(B) ≠ ∅:
    mark A ↔ B as conflicting
```

**Conflicting items** must run sequentially — the first to
merge wins, and later items rebase before continuing.

**Non-conflicting items** can run in parallel.

### Execution Order

1. **PRs ready to merge** — mark ready, monitor CI, merge
2. **PRs needing fixes** — fix review comments, rebase,
   push, monitor, merge
3. **Issues with no conflicts** — implement in parallel
   worktrees
4. **Issues with conflicts** — implement sequentially in
   dependency order

Present the execution plan as a numbered list showing
parallel groups and sequential chains:

```
Parallel group 1: PR #42 (ready), PR #55 (needs fixes)
Sequential chain: Issue #10 → Issue #15 (shared files)
Parallel group 2: Issue #20, Issue #25 (independent)
```

### Supervisor Gate

**Implicit approval bypass:** If the user's original input
contains explicit ordering or parallelism instructions,
skip the approval gate and proceed.

Otherwise:

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
Options:
- Approve plan (Recommended) — Start execution
- Edit — Describe changes to ordering or grouping

## Phase 3: Execute

Process items according to the approved plan.

### Processing PRs

For each PR, execute the pr-continuation play from
`Dev10x:work-on`:

1. Check out the PR branch (or work in existing worktree)
2. If review comments exist → `Dev10x:gh-pr-respond`
3. If conflicts with develop → rebase and resolve
4. `Dev10x:git-groom` to clean commit history
5. Mark ready via `gh pr ready`
6. Monitor CI — fix failures with fixup commits
7. When CI passes and no new comments → merge via
   `gh pr merge --squash --delete-branch`
8. After merge → rebase any downstream items that
   depend on this PR's changes

**Draft → Ready cycle:** PRs that revert to draft after
CI review posts comments need immediate `gh pr ready`
followed by merge attempt. Do not wait for another CI
cycle if the review is informational only.

### Processing Issues

For each issue (or parallel group of issues):

1. Create a worktree or branch per issue
2. Delegate to `Dev10x:work-on` with the issue URL
3. Monitor the resulting PR through to merge
4. After merge → update develop, rebase downstream items

**Parallel execution:** For non-conflicting issues, launch
subagents via:
```
Agent(subagent_type="general-purpose",
    description="Implement issue #N",
    prompt="...",
    run_in_background=true)
```

**Known limitation:** Agents with `isolation: "worktree"`
cannot use Write/Edit tools reliably. Use background agents
without worktree isolation, or implement sequentially in the
main session. See `Dev10x:work-on` Phase 4 parallelism
policy for details.

### Post-Merge Rebase

After merging any item, check if downstream items in the
same sequential chain are affected:

1. `git fetch origin develop`
2. For each active branch in the chain:
   `git rebase origin/develop`
3. If rebase conflicts → resolve, commit, force-push
4. If rebase succeeds → continue processing

### Progress Compaction

After completing each parallel group or sequential chain,
compact progress per `references/task-orchestration.md`
Pattern 8. Summarize completed items in task metadata to
free context for remaining work.

## Phase 4: Verify

After all items are processed:

1. Call `TaskList` to show the full task list
2. Verify all items are either merged, closed, or have
   research comments posted
3. Show summary table:

```
| Item | Type | Result |
|------|------|--------|
| PR #42 | PR | Merged |
| Issue #10 | Feature | PR #101 merged |
| Issue #20 | Research | Comment posted |
```

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
Options:
- Work complete — done (Recommended)
- Add more items
- Revisit an item

## Pause/Resume

At any pause signal, invoke `Dev10x:session-wrap-up`.
Active worktrees and in-progress PRs are bookmarked
automatically.

## Examples

### Example 1: Close all open loops

**User:** `/Dev10x:fanout`

Scans repo → finds 2 draft PRs and 5 open issues.
Classifies: PRs have no conflicts, 3 issues share files.
Plan: merge both PRs first (parallel), then issues in
2 parallel groups + 1 sequential chain.

### Example 2: Specific items

**User:** `/Dev10x:fanout #42 #55 GH-10 GH-15 GH-20`

Classifies the 5 items, builds conflict graph, presents
plan, executes.

### Example 3: PRs only

**User:** `/Dev10x:fanout PRs`

Scans only open PRs. Processes each to merge — mark ready,
monitor CI, fix comments, merge. Repeats until all merged.
