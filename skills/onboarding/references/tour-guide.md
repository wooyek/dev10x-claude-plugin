# Dev10x Onboarding Tour Guide

Detailed tour content loaded by the onboarding skill.

## Phase 1: Detect User Context

### 1.1 Experience Level

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
Options:
- New to Claude Code — First time using AI coding tools
- Know Claude Code, new to Dev10x — Familiar with Claude Code
- Returning user — Used Dev10x before, want a refresher

### 1.2 Configuration Detection

Check what's already set up (skip configured items in tour):

| Check | Command | Configured if |
|-------|---------|---------------|
| Git aliases | `git config alias.develop-log` | Non-empty |
| SKILLS.md | `test -f ~/.claude/SKILLS.md` | File exists |
| Global config | `ls ~/.claude/memory/Dev10x/` | Dir exists |
| Playbook overrides | `ls .claude/Dev10x/playbooks/*.yaml` | Found |
| Worktree | `test -f .git` | `.git` is file |

### 1.3 Project Detection

```bash
test -f pyproject.toml     # Python project
test -f package.json       # Node/frontend project
test -f Cargo.toml         # Rust project
```

## Phase 2: Guided Tour

### 2.1 Skill Discovery

```
Dev10x organizes 75+ skills into families:

Pipeline — End-to-end ticket-to-merge workflow
  /Dev10x:work-on <ticket-url>  <- Start here for any task

Git — Atomic commits with gitmoji and JTBD titles
  /Dev10x:git-commit

PR — Full PR lifecycle with CI monitoring
  /Dev10x:gh-pr-create -> /Dev10x:gh-pr-monitor

Session — Track work, defer items, resume later
  /Dev10x:session-wrap-up -> /Dev10x:park-discover

To see all skills: check ~/.claude/SKILLS.md
To regenerate: /Dev10x:skill-index
```

### 2.2 Git Workflow Setup

**Skip if:** Git aliases already configured.

```
Dev10x uses git aliases to avoid permission friction:
  git develop-log   — commits since diverging from develop
  git develop-diff  — diff since diverging from develop
  git develop-rebase — interactive rebase onto develop
```

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
Options:
- Set up aliases now (Recommended) — Run git-alias-setup
- Skip — I'll set them up later

If user chooses setup: `Skill(skill="Dev10x:git-alias-setup")`

### 2.3 PR Pipeline Demo

```
The Dev10x PR pipeline automates the full shipping flow:

1. /Dev10x:git-commit    — Gitmoji + JTBD commit message
2. /Dev10x:gh-pr-create  — Draft PR with Job Story
3. /Dev10x:gh-pr-monitor — Background CI + review monitoring
4. /Dev10x:git-groom     — Clean commit history
5. /Dev10x:gh-pr-respond — Address review comments

Or use /Dev10x:work-on <ticket> for the full pipeline.
```

### 2.4 Session Management

```
Dev10x tracks your work across sessions:

- /Dev10x:session-wrap-up — Save open work before closing
- /Dev10x:park            — Defer a task to the right place
- /Dev10x:park-discover   — Find deferred items at start
```

### 2.5 Customization

**Skip if:** Playbook overrides already exist.

```
Customize Dev10x behavior per project:

- Playbooks: Override workflow steps
  /Dev10x:playbook edit work-on feature

- Memory: Teach Dev10x about your project

- CLAUDE.md: Project-level instructions
```

### 2.6 Tour Summary

**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
Options:
- Start working — I have a task to begin (Recommended)
- Explore more — Show me additional capabilities
- Set up customization — Help me configure playbooks

## Phase 3: Setup Assistance (Optional)

Only runs if user chose "Explore more" or "Set up customization".

### If "Explore more":

Show additional families:
- Testing: `/test`, `/test:fix-flaky`, `/Dev10x:qa-scope`
- Architecture: `/Dev10x:adr-evaluate`, `/Dev10x:scope`
- Operations: `/Dev10x:investigate`, `/triage-sentry`
- Reports: `/work:daily`, `/work:weekly`

### If "Set up customization":

Guide through:
1. Creating a playbook override for most-used workflow
2. Setting up project memory with key context
3. Reviewing CLAUDE.md for project-specific instructions
