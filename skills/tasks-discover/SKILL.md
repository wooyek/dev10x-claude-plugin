---
name: dx:discover
description: >
  Use when checking for deferred items across all sources — so nothing
  is missed when starting a session or picking up where you left off.
user-invocable: true
invocation-name: dx:discover
---

# dx:discover — Gather Deferred Items

**Announce:** "Using dx:discover to check all deferral sources."

## When to Use

Invoke this skill when the user asks about existing deferred items:
- "what's deferred"
- "any open items from yesterday"
- "what do we have to pick up"
- "check for deferrals"

Do NOT use for writing new deferrals — use `dx:todo` or
`dx:defer` instead.

## Workflow

### 1. Detect context

```bash
date +%Y-%m-%d
git branch --show-current
basename "$(git rev-parse --show-toplevel)"
```

Determine the lookback date: default is yesterday. If the user
specifies a date or range, use that instead.

### 2. Check all deferral sources

Run all checks in parallel where possible. Report findings grouped
by source.

#### 2a. Project TODO file

Read `.claude/TODO.md` in the repo root. Extract pending items
(`- [ ]` lines). If the file doesn't exist, note "No project TODO
file."

#### 2b. Recent code TODOs

Grep for TODO/FIXME comments in source files:

```bash
grep -rn "TODO\|FIXME" src/ --include="*.py" | head -30
```

Adjust the path and file extension to match the project language.
Distinguish long-standing tech debt from recently added items by
checking `git log` for the lookback period.

#### 2c. Slack DM reminders

Search for bot-sent reminders using MCP Slack tools (read mode).

**Configure your bot's user ID first** — find it in Slack app
settings under "App credentials" → "Bot User OAuth Token" or by
calling `auth.test` on the token. Store it in project memory or
the plugin config.

```
slack_search_public_and_private
  query: "from:<@YOUR_BOT_USER_ID> 🔖 after:LOOKBACK_DATE"
  include_bots: true
  sort: timestamp
  sort_dir: desc
  limit: 20
```

The `🔖` emoji is the standard prefix from `dx:remind`.

If no results with `🔖`, broaden to:
```
from:<@YOUR_BOT_USER_ID> after:LOOKBACK_DATE defer OR TODO OR reminder
```

#### 2d. Memory files

Grep the project memory directory for in-progress or deferred items:

```bash
grep -rn "defer\|TODO\|in-progress\|pick up" \
  ~/.claude/projects/<encoded-path>/memory/ \
  --include="*.md" || true
```

#### 2e. Git log (recent commits)

Check for recent commits by the user in the lookback period:

```bash
git log --all --since="LOOKBACK_DATE" --oneline --author="<username>" \
  | head -20
```

This provides context on what was being worked on.

#### 2f. PR wrap-up reminders

Check open PRs for automated session bookmark comments posted by
`dx:wrap-up`. These are self-reminders left on PRs during
previous sessions:

```bash
gh pr list --author="@me" --state open \
  --json number,title,url --limit 10
```

For each PR, search for reminder comments with the standard prefix:

```bash
gh pr view {N} --json comments --jq '.comments[]
  | select(.body | test("🔖 \\*\\*Session bookmark\\*\\*"))
  | {body: .body[0:300], createdAt: .createdAt}'
```

The `🔖 **Session bookmark**` prefix is the standard marker set by
`dx:wrap-up`. Include matching comments in the findings under
"### PR Session Bookmarks".

### 3. Present findings

Group results by source in a scannable format:

```markdown
## Deferred Items — [project name]

### .claude/TODO.md
(items or "No project TODO file")

### Slack DM Reminders
(items or "None found")

### Recent Code TODOs
(items or "Only long-standing tech debt")

### Memory Notes
(items or "None")

### Recent Activity (context)
(recent commits or "No commits in lookback period")

### PR Session Bookmarks
(matching PR comments or "None found")
```

### 4. Offer next steps

If deferred items were found, ask:
- "Want to start working on any of these?"
- "Want me to check other repos too?" (if multi-repo context)

## Used By

- `dx:todo` — redirects here when user asks to review/check
  deferrals instead of write them
