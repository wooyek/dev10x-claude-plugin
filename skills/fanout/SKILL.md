---
name: Dev10x:fanout
description: >
  Close multiple open loops in parallel — PRs waiting for review,
  issues ready for implementation, tickets needing attention. Honors
  dependencies, minimizes conflict risk, auto-advances by default.
  TRIGGER when: 2+ independent work items need parallel processing
  (PRs, issues, tickets).
  DO NOT TRIGGER when: single task or sequential dependency chain
  (use Dev10x:work-on).
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
  - Skill(skill="Dev10x:skill-audit")
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
4. `TaskCreate(subject="Monitor: track PRs through merge", activeForm="Monitoring")`
5. `TaskCreate(subject="Verify: confirm all items resolved", activeForm="Verifying")`
6. `TaskCreate(subject="Audit: review session skill usage", activeForm="Auditing")`

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
issue numbers, or PR numbers. Classify each argument
independently:

| Pattern | Type | Action |
|---------|------|--------|
| `https://github.com/{owner}/{repo}/issues` | `scope:issues` | Restrict scan to issues only |
| `https://github.com/{owner}/{repo}/pulls` | `scope:pulls` | Restrict scan to PRs only |
| `https://github.com/{owner}/{repo}/issues/{N}` | `item:issue` | Fetch specific issue |
| `https://github.com/{owner}/{repo}/pull/{N}` | `item:pr` | Fetch specific PR |
| `#N` or bare number | `item` | Classify per `Dev10x:work-on` Phase 1 rules |
| `PRs`, `issues` (bare keyword) | `scope` | Restrict scan to matching type (same as scope URL) |
| Free text (anything else) | `note` | Parse intent to infer scope and work items (see below) |

**Free-text input:** When an argument doesn't match any URL,
number, or keyword pattern, treat it as a `note`. Analyze the
text to infer the user's intent:

- Identify scope hints (e.g., "merge all open PRs" → `scope:pulls`,
  "triage the bug reports" → `scope:issues`)
- Extract implicit item references (e.g., "fix the timeout bug
  from last week" → search recent issues)
- Determine parallelism intent (e.g., "split this into parallel
  tasks" → plan parallel processing)

Classification follows `Dev10x:work-on` Phase 1 `note` handling.
When scope cannot be inferred, default to scanning both PRs and
issues.

**Scope keywords and URLs** constrain the default scan.
When a scope URL is present, run only the matching `gh` command
instead of both:

- `scope:issues` → run `gh issue list` only, skip `gh pr list`
- `scope:pulls` → run `gh pr list` only, skip `gh issue list`

Scope URLs and specific items can be mixed. When both are
present, the scope restricts the default scan while specific
items are fetched regardless of scope:

```
/Dev10x:fanout https://github.com/org/repo/issues #42
```
→ Scan issues only (`gh issue list`) + fetch PR #42 explicitly.

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

**REQUIRED: Create one subtask per work item** under the Phase 3
parent task before starting any execution. Each subtask tracks
the lifecycle of a single issue or PR:

```
TaskCreate(subject="Process: PR #42 — fix payment routing",
    parentTaskId=phase3TaskId,
    metadata={"type": "pr-continuation", "item": "#42"})
TaskCreate(subject="Process: GH-10 — add retry mechanism",
    parentTaskId=phase3TaskId,
    metadata={"type": "feature", "item": "GH-10"})
```

Mark each subtask `in_progress` when starting and `completed`
when the item's PR is merged or work is handed off.

### Pre-Item Self-Check (REQUIRED)

Before processing **each** work item, execute this two-step gate:

1. **Branch verification:** Run `git symbolic-ref --short HEAD`
   and confirm the current branch matches the expected item.
   If it does not, create or switch to the correct branch
   before proceeding. This prevents commits landing on the
   wrong branch when processing items sequentially.

2. **Delegation check:** STOP and ask yourself: "Am I about to
   implement this item directly?" If yes, invoke
   `Skill(skill="Dev10x:work-on", args="<item-url>")` instead.
   Fanout is an **orchestrator**, not an implementor.

Skipping either step causes cascading errors — wrong-branch
commits require destructive `git reset --hard` cleanup, and
inline implementation bypasses work-on's structured lifecycle
(branch setup, code review, shipping pipeline).

### Work-On Delegation

**REQUIRED: Every issue MUST be delegated to `Dev10x:work-on`.**
Do NOT implement issues inline within the fanout session. Fanout
dispatches work to `Dev10x:work-on` and tracks results. Inline
implementation bypasses work-on's structured lifecycle (branch
setup, Job Story, code review, shipping pipeline) and produces
untracked work.

**Enforcement:**
- Each issue → `Skill(skill="Dev10x:work-on", args="<issue-url>")`
- Each PR → `Skill(skill="Dev10x:work-on", args="<pr-url>")`
- After work-on completes → invoke `Dev10x:gh-pr-monitor` to
  track the resulting PR through CI and merge

### Processing PRs

For each PR, delegate to `Dev10x:work-on` with the PR URL.
Work-on executes the pr-continuation play:

1. Check out the PR branch (or work in existing worktree)
2. If review comments exist → `Dev10x:gh-pr-respond`
3. If conflicts with develop → rebase and resolve
4. `Dev10x:git-groom` to clean commit history
5. Mark ready via `gh pr ready`
6. Monitor CI — fix failures with fixup commits
7. When CI passes and no new comments → merge via
   `gh pr merge <MERGE_STRATEGY> --delete-branch`
   (see Merge Strategy below)
8. After merge → rebase any downstream items that
   depend on this PR's changes

**Draft → Ready cycle:** PRs that revert to draft after
CI review posts comments need immediate `gh pr ready`
followed by merge attempt. Do not wait for another CI
cycle if the review is informational only.

### Processing Issues

For each issue (or parallel group of issues):

1. Create a worktree or branch per issue
2. **REQUIRED:** Delegate to `Dev10x:work-on` with the issue URL
3. After work-on completes → invoke `Dev10x:gh-pr-monitor`
   to track the resulting PR through CI and merge
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

### Merge Strategy

The merge command uses a configurable strategy flag. Resolution
order (first match wins):

1. **Playbook override:** `merge_strategy` in the user's
   `work-on.yaml` playbook (e.g., `merge_strategy: rebase`)
2. **Memory note:** user feedback memory mentioning merge
   preference (e.g., "prefer --rebase")
3. **Default:** `--rebase` — preserves groomed commit history
   and minimizes stacked-branch friction

| Strategy | Flag | When to use |
|----------|------|-------------|
| Rebase | `--rebase` | Default — atomic commits preserved |
| Squash | `--squash` | Single-commit PRs or messy history |
| Merge commit | `--merge` | Protected branches requiring merge |

### Stacked-Branch Merge Protocol

When merging stacked PRs (PR B depends on PR A's branch),
squash merges rewrite history and make downstream PRs
unmergeable. Follow this protocol:

1. Merge the base PR (A) using the configured strategy
2. `git fetch origin develop`
3. For each downstream PR (B):
   - `git checkout <branch-B>`
   - `git rebase origin/develop`
   - If conflicts → resolve, commit, force-push
   - Wait for CI to pass on the rebased branch
4. Merge downstream PR (B)
5. Repeat for further stacked PRs

**Note:** `--rebase` merge minimizes this friction compared
to `--squash` because the base commits remain intact.

### Progress Compaction

After completing each parallel group or sequential chain,
compact progress per `references/task-orchestration.md`
Pattern 8. Summarize completed items in task metadata to
free context for remaining work.

## Phase 4: Monitor

After all items have been processed in Phase 3, track every
PR created during this session through to merge.

**REQUIRED: Create one subtask per PR** under the Phase 4
parent task:

```
TaskCreate(subject="Monitor: PR #101 — GH-10 implementation",
    parentTaskId=phase4TaskId)
```

For each PR:
1. Invoke `Dev10x:gh-pr-monitor` to watch CI and review status
2. If CI fails → fix with fixup commits, push, re-monitor
3. If new review comments → delegate to `Dev10x:gh-pr-respond`
4. When CI passes and PR is approved → merge via
   `gh pr merge <MERGE_STRATEGY> --delete-branch`
   (see Merge Strategy below)
5. After merge → rebase downstream branches if needed

Mark each subtask `completed` when the PR is merged or
handed off for external review.

## Phase 5: Verify

After all items are processed and PRs merged:

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

## Phase 6: Audit

**Phase 6 is REQUIRED when the session processes 3 or more
work items.** "Fewer than 3" means exactly 0, 1, or 2 items.
Do not add qualifiers like "independent" or "unique" to
justify skipping — count all items processed, regardless of
type or complexity.

**REQUIRED:** Invoke `Skill(skill="Dev10x:skill-audit")` to
analyze skill usage, compliance rates, and identify process
improvements.

**Skip this phase** only when the session processed 0, 1, or
2 work items, or when the user explicitly declines.

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
