---
name: Dev10x:verify-acc-dod
description: >
  Verify that definition-of-done / acceptance criteria are met before
  closing a task list. Reads playbook-specific criteria from YAML,
  checks actual state (CI, PR, working copy), and prompts the user
  to confirm completion. Use when an agent completes its task list
  and needs to verify the work is shippable.
user-invocable: true
invocation-name: Dev10x:verify-acc-dod
allowed-tools:
  - AskUserQuestion
  - Bash(gh:*)
---

# Verify Acceptance Criteria / Definition of Done

**Announce:** "Verifying acceptance criteria for this work session."

## When to Use

- As the final step in any orchestrating skill's task list
  (work-on, fanout, gh-pr-monitor)
- When the user asks "is this done?" or "are we ready to ship?"
- Before closing a task list or handing off work

## Orchestration

This skill follows `references/task-orchestration.md` patterns
(Tier: Minimal).

**REQUIRED: Create a task at invocation.** Execute at startup:

1. `TaskCreate(subject="Verify acceptance criteria", activeForm="Verifying acceptance criteria")`

Mark completed when done.

## Input

The skill accepts an optional `work_type` argument. If not
provided, infer from session context:

| Context | Work type |
|---------|-----------|
| Ticket with implementation | `feature` |
| Sentry/bug ticket | `bugfix` |
| PR with review comments | `pr-continuation` |
| No ticket, no PR | `local-only` |
| Sentry/Slack only, no fix planned | `investigation` |
| Fanout (multi-item) | `fanout` |

## Criteria Resolution

Read the acceptance criteria YAML file:

```
~/.claude/projects/<project>/memory/acceptance-criteria.yaml
```

**Resolve criteria** in this order:
1. Check `overrides` for a matching `work_type` with
   `persist: false` — use if found, then **remove** the entry
2. Check `overrides` for a matching `work_type` with
   `persist: true` — use if found
3. Fall back to `defaults[work_type].criteria` from the file
4. If the file is absent or the work type has no entry, use
   the hardcoded defaults below

**Hardcoded defaults:**

```yaml
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
  fanout:
    criteria: >
      All child work items have merged PRs or documented
      outcomes. No orphaned branches or draft PRs remaining.
```

## Verification Checks

After resolving the criteria text, run automated checks
against the actual state:

| Check | Command | Pass condition |
|-------|---------|----------------|
| Clean working copy | `git status --porcelain` | No output |
| CI passing | `gh pr checks` | All checks pass |
| PR not draft | `gh pr view --json isDraft` | `isDraft: false` |
| No open review threads | `gh pr view --json reviewDecision` | Not `CHANGES_REQUESTED` |

**Skip PR checks** for `local-only` and `investigation` types.

**For `fanout` type:** Instead of PR checks, verify each child
work item's PR is merged:
```bash
gh pr list --state merged --json number,title
```

Report which checks pass and which fail.

## Presentation

Present the resolved criteria alongside check results:

```
Acceptance criteria (feature):
  PR passing CI, groomed history, review published

Checks:
  ✅ Working copy clean
  ✅ CI passing (3/3 checks)
  ✅ PR marked ready
  ❌ Review decision: CHANGES_REQUESTED

1 check failed. Address before completing?
```

## Decision Gate

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
Options:
- **"Work complete" (Recommended)** — All criteria met, close
  the task list
- **"Override — complete anyway"** — Accept despite failures
  (ask whether to persist this override)
- **"Go back"** — Return to fix failing checks

If the user picks "Override", ask whether to persist:

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
Options:
- **"Always"** — Save override with `persist: true`
- **"Just this time"** — Save with `persist: false`

Update the YAML file accordingly. Create the file if absent.

## Integration

```
Dev10x:work-on → ... → Dev10x:verify-acc-dod (last step)
Dev10x:fanout  → ... → Dev10x:verify-acc-dod (last step)
```

Callers pass the work type and let this skill handle criteria
resolution, state checking, and user confirmation.
