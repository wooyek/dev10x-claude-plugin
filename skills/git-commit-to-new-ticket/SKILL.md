---
name: dx:git-commit-to-new-ticket
description: Convert existing git commits into issue tracker tickets with proper branch management and commit message formatting. Use this skill when a commit needs to be retroactively tracked, typically for tech debt fixes, bug fixes, or improvements that were committed without a ticket reference. This skill automates the workflow of creating the ticket, branching, cherry-picking, and updating the commit message.
user-invocable: true
invocation-name: dx:git-commit-to-new-ticket
---

# Commit to Ticket

## Overview

This skill automates the process of converting an existing git commit into a tracked ticket with proper tracking. It creates a ticket from the commit's changes, creates a properly named branch, cherry-picks the commit, and updates the commit message to reference the new ticket.

## Prerequisites Check

**IMPORTANT:** This skill uses the `ticket:create` skill which supports GitHub Issues, Linear, and JIRA.

## When to Use This Skill

Use this skill when:
- A commit was made without a ticket reference
- Tech debt or bug fixes need to be tracked retroactively
- A commit needs proper documentation in the issue tracker
- A commit needs to be moved to a feature branch with ticket tracking

## Workflow

### Step 1: Show Recent Commits (if no commit hash provided)

If the user does not provide a commit hash, show the last 20 commits for selection:

```bash
git log --oneline -20
```

### Step 2: Analyze the Commit

Examine the commit to understand what problem it solves:

```bash
git show <commit-hash>
```

### Step 3: Create Ticket

Use the `ticket:create` skill to create a properly structured ticket from the commit.

### Step 4: Create Branch

Use the `ticket:branch` skill to create a properly named branch.

### Step 5: Cherry-pick Commit

Cherry-pick the original commit to the new branch:

```bash
git cherry-pick <commit-hash>
```

### Step 6: Update Commit Message

Amend the commit message to reference the new ticket.

### Step 7: Verify Result

Show the updated commit and verify changes.

### Step 8: Push and Create PR (Optional)

Use the `dx:gh-pr-create` skill to push the branch and create a PR.

## Integration with Other Skills

```
dx:git-commit-to-new-ticket
├── Uses: ticket:create (Step 3)
├── Uses: ticket:branch (Step 4)
└── Uses: dx:gh-pr-create (Step 8, optional)
```
