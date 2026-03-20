---
name: Dev10x:gh-pr-request-review
description: Request review on a GitHub PR from teams or users
user-invocable: true
invocation-name: Dev10x:gh-pr-request-review
allowed-tools:
  - Bash(~/.claude/tools/gh-request-review.py:*)
  - Bash(gh repo view:*)
  - Bash(yq:*)
  - AskUserQuestion
---

## Orchestration

This skill follows `references/task-orchestration.md` patterns.
Create a task at invocation, mark completed when done:

**REQUIRED: Create a task at invocation.** Execute at startup:

1. `TaskCreate(subject="Request PR review", activeForm="Requesting review")`

Mark completed when done: `TaskUpdate(taskId, status="completed")`

Request reviews on GitHub pull requests from teams or individual users.
Auto-resolves reviewers from per-project config when available.

## Reviewer Resolution

The skill resolves reviewers in this order:

1. **Explicit argument** — if the user passes reviewer names, use those
2. **Config file** — read `~/.claude/memory/github-reviewers-config.yaml`
   and look up the current repo's project entry
3. **Ask the user** — if no config entry exists and `default_action: ask`

### Config file format

The config file is optional. If it does not exist or lacks an entry
for the current repo, the skill falls back to `default_action`
behavior (ask or skip).

```yaml
# ~/.claude/memory/github-reviewers-config.yaml
default_action: ask  # "skip" or "ask" for unconfigured projects

projects:
  tt-pos:
    reviewers:
      - tiretutorinc/backend-devs
  Dev10x-ai:
    skip: true
```

- Keys are GitHub repo short names (last segment of `owner/repo`)
- `reviewers` list uses GitHub format: `org/team-slug` for teams,
  `username` for individual users
- `skip: true` suppresses the review request for that project
- `default_action: ask` prompts the user for unconfigured projects;
  `skip` silently skips them

### Resolution workflow

1. Detect the current repo: `gh repo view --json name --jq .name`
2. Read and parse the config file using `yq`:
   `yq '.projects["REPO_NAME"]' ~/.claude/memory/github-reviewers-config.yaml`
3. Look up the repo name in `projects`:
   - **Found with `skip: true`** → print "Skipping review request
     for {repo}" and stop
   - **Found with `reviewers` list** → use those reviewers
   - **Not found, `default_action: ask`** → **REQUIRED: Call
     `AskUserQuestion`** to ask the user who to request review
     from (do NOT use plain text)
   - **Not found, `default_action: skip`** → print "No reviewers
     configured for {repo}, skipping" and stop
4. Call `gh-request-review.py` with the resolved reviewers

## Usage

### Auto-resolve from config (no arguments)

Invoke the skill without arguments. It reads the config, detects
the current repo, and requests review from the configured reviewers:

```
/Dev10x:gh-pr-request-review
```

### Explicit reviewers (override config)

Pass reviewer names directly to skip config lookup:

```bash
~/.claude/tools/gh-request-review.py \
  --pr PR_NUMBER \
  --reviewer org-name/team-slug
```

```bash
~/.claude/tools/gh-request-review.py \
  --pr PR_NUMBER \
  --reviewer user1 \
  --reviewer user2
```

### With verification

```bash
gh pr view PR_NUMBER --json reviewRequests \
  --jq '.reviewRequests[].login // .reviewRequests[].name'
```

## Notes

- Use `gh-request-review.py` for requesting reviews (handles both
  users and teams)
- Team format: `org-name/team-slug`
- The script itself stays CLI-only — config awareness lives in the
  skill layer, not the script
- Verify the review request was assigned by checking `reviewRequests`
