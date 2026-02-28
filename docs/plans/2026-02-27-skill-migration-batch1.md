# Skill Migration Batch 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Copy 7 dev10x skills (+ skill:audit as dev10x:skill-audit) from
`~/.claude/skills/` into the plugin repo, sanitized of all project-specific
content, one atomic commit per skill.

**Architecture:** Each skill maps to a directory under `skills/` in the
plugin. SKILL.md is the main content; scripts go in `scripts/` subdirectory.
All project-specific strings (org names, ticket IDs, emails, Slack IDs, real
branch names) are replaced with generic ecommerce placeholders. Scripts are
made executable.

**Tech Stack:** Bash, git, Write/Edit tools. No build step. No tests
(skills are prose documents, not code). Verification: read back the written
file and confirm no project refs remain.

---

## Sanitization Reference

Apply these replacements across ALL files (SKILL.md + scripts):

| Pattern | Replacement |
|---------|-------------|
| `tiretutorinc/tt-pos` | `your-org/your-repo` |
| `tiretutorinc/tt-backend` | `your-org/your-backend` |
| `Brave-Labs/zebra` | `your-org/your-repo` |
| `janusz/PAY-616/tt-pos-6/remove-database-constraint` | `user/TICKET-616/feature-description` |
| `PAY-616`, `PAY-133`, `PAY-58`, `SHOP-42` | `TICKET-123` |
| `janusz@tiretutor.com` | `dev@example.com` |
| `skill:audit` (skill name) | `dev10x:skill-audit` |
| `tt:` namespace in examples | remove (or replace with generic namespace) |
| `debug:` namespace in examples | remove |

---

## Task 1: dev10x:tasks

**Files:**
- Create: `skills/dev10x:tasks/SKILL.md`

No scripts, no sanitization beyond one example ticket ID.

**Step 1: Create directory and write SKILL.md**

Write `skills/dev10x:tasks/SKILL.md` with this content (sanitize `SHOP-42`
→ `TICKET-42`):

```markdown
---
name: dev10x:tasks
description: >
  Use when tracking in-session work items — so open loops are visible
  and triageable before session end without losing track of parallel work.
user-invocable: true
invocation-name: dev10x:tasks
---

# dev10x:tasks — In-Session Task Tracking

**Announce:** "Using dev10x:tasks to [show/add/update] session tasks."

## Overview

Thin wrapper around Claude's `TaskCreate`/`TaskUpdate`/`TaskList` tools
for tracking work items within the current session.

## Commands

### Show tasks

Use `TaskList` to display all current tasks grouped by status.
Present as a markdown table:

| # | Status | Task |
|---|--------|------|
| 1 | in_progress | Write payment integration |
| 2 | pending | Create PR for TICKET-42 |
| 3 | completed | Add webhook endpoint |

### Add task

Use `TaskCreate` with:
- `subject`: short task title
- `description`: context, file paths, or links if available

### Update task

Use `TaskUpdate` with the task ID and new `status`:
- `in_progress` — currently working on
- `completed` — done
- `pending` — deferred within this session

## Used By

- `dev10x:defer` — when user picks "keep for this session"
- `dev10x:wrap-up` — Phase 1 auto-scan reads the task list
```

**Step 2: Verify — grep for project-specific strings**

Run:
```bash
grep -n "SHOP\|tiretutor\|janusz\|PAY-\|tiretutorinc" skills/dev10x:tasks/SKILL.md
```
Expected: no output (no matches).

**Step 3: Commit**

```bash
git add skills/dev10x:tasks/SKILL.md
git commit -m "✨ Add dev10x:tasks skill"
```

---

## Task 2: dev10x:git (with 3 scripts)

**Files:**
- Create: `skills/dev10x:git/SKILL.md`
- Create: `skills/dev10x:git/scripts/git-push-safe.sh`
- Create: `skills/dev10x:git/scripts/git-rebase-groom.sh`
- Create: `skills/dev10x:git/scripts/git-seq-editor.sh`

No sanitization needed — all files are clean of project refs.
One minor update: `git-seq-editor.sh` comment references old skill name
`git:safe/scripts/` — update to `dev10x:git/scripts/`.

**Step 1: Create directories**

```bash
mkdir -p skills/dev10x:git/scripts
```

**Step 2: Write SKILL.md**

Copy `~/.claude/skills/dev10x:git/SKILL.md` verbatim. The content is clean.
The `settings.local.json` snippet references `~/.claude/skills/dev10x:git/`
which is the user's local path — that is correct as-is (plugin skills install
to `~/.claude/skills/` anyway).

**Step 3: Write the 3 scripts**

Copy the following files verbatim from `~/.claude/skills/dev10x:git/scripts/`:
- `git-push-safe.sh` — no project refs
- `git-rebase-groom.sh` — no project refs
- `git-seq-editor.sh` — update comment on line 5:
  Change `git:safe/scripts/git-seq-editor.sh`
  to `dev10x:git/scripts/git-seq-editor.sh`

**Step 4: Make scripts executable**

```bash
chmod +x skills/dev10x:git/scripts/git-push-safe.sh
chmod +x skills/dev10x:git/scripts/git-rebase-groom.sh
chmod +x skills/dev10x:git/scripts/git-seq-editor.sh
```

**Step 5: Verify**

```bash
grep -rn "tiretutor\|janusz\|PAY-\|tiretutorinc\|git:safe" skills/dev10x:git/
```
Expected: no output.

**Step 6: Commit**

```bash
git add skills/dev10x:git/
git commit -m "✨ Add dev10x:git skill with safe push and rebase scripts"
```

---

## Task 3: dev10x:skill-create

**Files:**
- Create: `skills/dev10x:skill-create/SKILL.md`

No scripts. One sanitization: remove `tt:` and `debug:` from the active
namespaces list (those are project-specific).

**Step 1: Create directory**

```bash
mkdir -p skills/dev10x:skill-create
```

**Step 2: Write SKILL.md**

Copy `~/.claude/skills/dev10x:skill-create/SKILL.md` with this change:

Line: `Active namespaces: \`dev10x:\`, \`ticket:\`, \`pr:\`, \`commit:\`, \`tt:\`, \`debug:\``

Change to: `Active namespaces: \`dev10x:\`, \`ticket:\`, \`pr:\`, \`commit:\``

Everything else is clean.

**Step 3: Verify**

```bash
grep -n "tt:\|debug:\|tiretutor\|janusz\|PAY-\|tiretutorinc" skills/dev10x:skill-create/SKILL.md
```
Expected: no output.

**Step 4: Commit**

```bash
git add skills/dev10x:skill-create/SKILL.md
git commit -m "✨ Add dev10x:skill-create skill"
```

---

## Task 4: dev10x:skill-audit (renamed from skill:audit)

**Files:**
- Create: `skills/dev10x:skill-audit/SKILL.md`
- Create: `skills/dev10x:skill-audit/scripts/extract-session.sh`
- Create: `skills/dev10x:skill-audit/scripts/extract-session.py`

Sanitize SKILL.md:
- All `skill:audit` occurrences → `dev10x:skill-audit`
- `PAY-58 audit` → `TICKET-58 audit`
- `PAY-133` → `TICKET-123`

Scripts: `extract-session.py` is clean (pure stdlib Python, no project refs).
`extract-session.sh` calls `python3` directly — keep as-is (the skill is
invoked via the sh wrapper which is the pre-approved path).

**Step 1: Create directories**

```bash
mkdir -p skills/dev10x:skill-audit/scripts
```

**Step 2: Write SKILL.md**

Copy `~/.claude/skills/skill:audit/SKILL.md` applying these substitutions:
- `skill:audit` → `dev10x:skill-audit` (name in frontmatter, invocation-name,
  all prose references)
- `allowed-tools` paths: `~/.claude/skills/skill:audit/scripts/:*` →
  `~/.claude/skills/dev10x:skill-audit/scripts/:*`
- `~/.claude/projects/<encoded-cwd>/*.jsonl` → keep (generic)
- `PAY-58 audit` → `TICKET-58 audit`
- `PAY-133` in examples → `TICKET-123`
- All other references (`~/.claude/skills/`, `settings.local.json`, etc.)
  are generic — keep as-is.
- In `allowed-tools`, update the Read/Write/Edit paths to remove
  `/home/janusz/` — use `~/.claude/**` only (these paths are user-local).

**Step 3: Write extract-session.sh**

Copy `~/.claude/skills/skill:audit/scripts/extract-session.sh` and update the
comment on the last line that calls python3:

Change: `exec python3 "$SCRIPT_DIR/extract-session.py" "$@"`
This is intentional — the .sh wrapper is the pre-approved entrypoint.
Keep as-is (no sanitization needed).

**Step 4: Write extract-session.py**

Copy `~/.claude/skills/skill:audit/scripts/extract-session.py` verbatim.
The file is clean — no project refs.

Note: the shebang is `#!/usr/bin/env python3`. This is called via the
.sh wrapper, so it works. Leave as-is.

**Step 5: Make scripts executable**

```bash
chmod +x skills/dev10x:skill-audit/scripts/extract-session.sh
chmod +x skills/dev10x:skill-audit/scripts/extract-session.py
```

**Step 6: Verify**

```bash
grep -rn "skill:audit\|/home/janusz\|janusz\|tiretutor\|PAY-\|SHOP-" skills/dev10x:skill-audit/
```
Expected: no output.

**Step 7: Commit**

```bash
git add skills/dev10x:skill-audit/
git commit -m "✨ Add dev10x:skill-audit skill (renamed from skill:audit)"
```

---

## Task 5: dev10x:gh (with 4 scripts)

**Files:**
- Create: `skills/dev10x:gh/SKILL.md`
- Create: `skills/dev10x:gh/scripts/gh-pr-detect.sh`
- Create: `skills/dev10x:gh/scripts/detect-tracker.sh`
- Create: `skills/dev10x:gh/scripts/gh-issue-get.sh`
- Create: `skills/dev10x:gh/scripts/gh-issue-comments.sh`

Sanitize:
- SKILL.md: example output block with `tiretutorinc/tt-pos` and `janusz/PAY-616/...`
- SKILL.md: `Brave-Labs/zebra` → `your-org/your-repo`
- `gh-pr-detect.sh`: example output comments (lines 9-11)
- `detect-tracker.sh`: `Brave-Labs/zebra` in comment (line 14)

**Step 1: Create directories**

```bash
mkdir -p skills/dev10x:gh/scripts
```

**Step 2: Write SKILL.md**

Copy `~/.claude/skills/dev10x:gh/SKILL.md` with these changes:

In the `gh-pr-detect.sh` output example block, replace:
```
PR_NUMBER=1323
REPO=tiretutorinc/tt-pos
PR_URL=https://github.com/tiretutorinc/tt-pos/pull/1323
BRANCH=janusz/PAY-616/tt-pos-6/remove-database-constraint
```
with:
```
PR_NUMBER=123
REPO=your-org/your-repo
PR_URL=https://github.com/your-org/your-repo/pull/123
BRANCH=user/TICKET-616/feature-description
```

In the `detect-tracker.sh` output example, replace:
```
FIXES_URL=https://github.com/Brave-Labs/zebra/issues/15
```
with:
```
FIXES_URL=https://github.com/your-org/your-repo/issues/15
```

**Step 3: Write gh-pr-detect.sh**

Copy `~/.claude/skills/dev10x:gh/scripts/gh-pr-detect.sh` and update comment
lines 9-11 (example output comments):
```
#   REPO=tiretutorinc/tt-pos
#   PR_URL=https://github.com/tiretutorinc/tt-pos/pull/1323
#   BRANCH=janusz/PAY-616/tt-pos-6/remove-database-constraint
```
Replace with:
```
#   REPO=your-org/your-repo
#   PR_URL=https://github.com/your-org/your-repo/pull/123
#   BRANCH=user/TICKET-616/feature-description
```

**Step 4: Write detect-tracker.sh**

Copy `~/.claude/skills/dev10x:gh/scripts/detect-tracker.sh` and update
comment line 14:
```
#   FIXES_URL=https://github.com/Brave-Labs/zebra/issues/15
```
Replace with:
```
#   FIXES_URL=https://github.com/your-org/your-repo/issues/15
```

**Step 5: Write gh-issue-get.sh and gh-issue-comments.sh**

Copy both verbatim — no project refs.

**Step 6: Make scripts executable**

```bash
chmod +x skills/dev10x:gh/scripts/gh-pr-detect.sh
chmod +x skills/dev10x:gh/scripts/detect-tracker.sh
chmod +x skills/dev10x:gh/scripts/gh-issue-get.sh
chmod +x skills/dev10x:gh/scripts/gh-issue-comments.sh
```

**Step 7: Verify**

```bash
grep -rn "tiretutor\|janusz\|PAY-\|tiretutorinc\|Brave-Labs\|bravelabs" skills/dev10x:gh/
```
Expected: no output.

**Step 8: Commit**

```bash
git add skills/dev10x:gh/
git commit -m "✨ Add dev10x:gh skill with PR and issue detection scripts"
```

---

## Task 6: dev10x:skill-motd (with script + dependencies.txt)

**Files:**
- Create: `skills/dev10x:skill-motd/SKILL.md`
- Create: `skills/dev10x:skill-motd/scripts/generate-motd.sh`
- Create: `skills/dev10x:skill-motd/dependencies.txt`

The SKILL.md is clean. The script is clean. The `dependencies.txt` has
project-specific skill names — include a sanitized version with only
the generic cross-skill dependencies that apply to this plugin.

**Step 1: Create directories**

```bash
mkdir -p skills/dev10x:skill-motd/scripts
```

**Step 2: Write SKILL.md**

Copy `~/.claude/skills/dev10x:skill-motd/SKILL.md` verbatim. It's clean.

**Step 3: Write generate-motd.sh**

Copy `~/.claude/skills/dev10x:skill-motd/scripts/generate-motd.sh` verbatim.
It uses `${HOME}/.claude/skills` — generic, correct.

**Step 4: Write sanitized dependencies.txt**

The original has project-specific skill dependencies. Write a clean version
that only includes the plugin's own skill graph:

```
# Skill dependency map: skill|dep1,dep2,...
# Only list direct orchestration dependencies (skill A invokes skill B).
# Maintain this when adding new orchestrating skills.
dev10x:wrap-up|dev10x:tasks,dev10x:defer,dev10x:todo
dev10x:defer|dev10x:tasks,dev10x:todo,dev10x:remind
dev10x:todo|dev10x:defer,dev10x:todo-review
```

**Step 5: Make script executable**

```bash
chmod +x skills/dev10x:skill-motd/scripts/generate-motd.sh
```

**Step 6: Verify**

```bash
grep -rn "tiretutor\|janusz\|PAY-\|tiretutorinc\|tt-db\|tt:e2e\|work:weekly\|tiretutor-slides" skills/dev10x:skill-motd/
```
Expected: no output.

**Step 7: Commit**

```bash
git add skills/dev10x:skill-motd/
git commit -m "✨ Add dev10x:skill-motd skill with MOTD generation script"
```

---

## Task 7: Commit design document

The design doc was created during brainstorming. Commit it now.

**Step 1: Commit**

```bash
git add docs/plans/
git commit -m "📝 Add skill migration design docs"
```

---

## Verification Checklist

After all 7 commits, run a final sweep:

```bash
grep -rn "tiretutor\|janusz\|bravelabs\|tiretutorinc\|PAY-\|SHOP-\|tt-pos\|tt-backend\|/home/janusz" skills/
```
Expected: no output.

Check all scripts are executable:
```bash
find skills/ -name "*.sh" -o -name "*.py" | xargs ls -la | grep -v "^-rwx"
```
Expected: all files show `rwx` execute bit.
