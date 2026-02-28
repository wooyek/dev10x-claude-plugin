---
name: dx:remind
description: >
  Use when you need a reminder to surface in Slack later — so deferred
  items appear when you are clearing messages, not buried in a file
  you might not open.
user-invocable: true
invocation-name: dx:remind
---

# dx:remind — Slack DM Reminder

**Announce:** "Using dx:remind to send a Slack reminder to yourself."

## Overview

Send a self-DM via Slack with a deferred item, formatted with session
context so you know where to pick it up.

## Prerequisites

- Slack token available (env `SLACK_BOT_TOKEN` or system keyring)
- A Slack notification helper script configured for your project
  (see `dx:slack` for the canonical sender pattern)

## Workflow

### 1. Gather context

```bash
git branch --show-current
basename "$(git rev-parse --show-toplevel)"
date +%Y-%m-%d
```

Extract from branch name:
- Ticket ID (pattern: `username/TICKET-ID/description`)
- Project name (from repo root basename)

### 2. Format message

Build the reminder message:

```
🔖 Deferred from session [YYYY-MM-DD]
Project: <project-name> | Branch: <branch-name>

<user's deferred item text>
```

If the user provided a URL or file reference, include it on a
separate line after the item text.

### 3. Send DM

For multi-line messages, write the formatted text to a temp file
using the Write tool first, then pass it via command substitution:

```bash
<path-to-slack-notify-script> --remind "$(cat /tmp/claude/remind-msg.txt)"
```

The Slack notify script should:
- Read `SLACK_BOT_TOKEN` from environment or system keyring
- Send the message as a self-DM (to the bot's own user)
- Prefix with `🔖` for easy search later

Do NOT use heredoc (`cat <<'EOF'`) to build the message inline —
bash security hooks may block it. Always use Write tool → temp file
→ `$(cat ...)` for multi-line content.

### 4. Confirm

Report to user: "Sent reminder to your Slack DMs."

## Standalone Usage

When invoked directly: `/dx:remind "message text"`

Parse the argument as the item text. Gather context and send.

## Used By

- `dx:defer` — when user picks "Slack DM to self"
