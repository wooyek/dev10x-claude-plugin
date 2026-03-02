# Skill Rename Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans
> to implement this plan task-by-task.

**Goal:** Rename 12 skill directories and invocation names per the
taxonomy in `2026-03-02-skill-rename-design.md`.

**Architecture:** Each rename is a `git mv` of the directory, then a
sweep of `name:`/`description:` fields in the renamed SKILL.md, then
a sweep of cross-references in other skills, rules, docs, and
dependency tracking files. Renames are grouped into independent
batches that can each be committed atomically.

**Tech Stack:** git, grep, sed (for bulk find-replace verification)

---

## Rename Map (quick reference)

| Old Dir | New Dir | Old Invoke | New Invoke |
|---|---|---|---|
| `gh` | `gh-context` | `dx:gh` | `dx:gh-context` |
| `gh-pr-comment-fixup` | `gh-pr-fixup` | `dx:gh-pr-comment-fixup` | `dx:gh-pr-fixup` |
| `git-branch-groom` | `git-groom` | `dx:git-branch-groom` | `dx:git-groom` |
| `ticket-from-commit` | `git-promote` | `dx:ticket:from-commit` | `dx:git-promote` |
| `tasks-defer` | `park` | `dx:defer` | `dx:park` |
| `tasks-todo` | `park-todo` | `dx:todo` | `dx:park-todo` |
| `tasks-remind` | `park-remind` | `dx:remind` | `dx:park-remind` |
| `tasks-discover` | `park-discover` | `dx:discover` | `dx:park-discover` |
| `tasks` | `session-tasks` | `dx:tasks` | `dx:session-tasks` |
| `tasks-wrap-up` | `session-wrap-up` | `dx:wrap-up` | `dx:wrap-up` |
| `skill-motd` | `skill-index` | `dx:skill-motd` | `dx:skill-index` |

---

## Task 1: Rename `gh` → `gh-context`

**Files:**
- Rename: `skills/gh/` → `skills/gh-context/`
- Modify: `skills/gh-context/SKILL.md` (name + description + script paths)
- Modify: `skills/gh-pr-monitor/SKILL.md` (allowed-tools path, script refs)
- Modify: `skills/gh-pr-create/SKILL.md` (allowed-tools path, script refs)

**Step 1: Move directory**

```bash
git mv skills/gh skills/gh-context
```

**Step 2: Update SKILL.md name field**

In `skills/gh-context/SKILL.md`, change:
- `name: dx:gh` → `name: dx:gh-context`
- All `~/.claude/skills/gh/scripts/` → `~/.claude/skills/gh-context/scripts/`
- All `Bash(~/.claude/skills/gh/scripts/` → `Bash(~/.claude/skills/gh-context/scripts/`

**Step 3: Update cross-references in other skills**

Grep for `skills/gh/` and `dx:gh` (exact match, not `dx:gh-pr`) in:
- `skills/gh-pr-monitor/SKILL.md` — update allowed-tools path and
  script references from `~/.claude/skills/gh/scripts/` to
  `~/.claude/skills/gh-context/scripts/`
- `skills/gh-pr-create/SKILL.md` — same pattern

**Step 4: Verify no remaining references**

```bash
grep -r "skills/gh/" skills/ --include="*.md"
grep -rw "dx:gh[^-]" skills/ --include="*.md"
```

Expected: no matches (only `dx:gh-context` and `dx:gh-pr-*`)

**Step 5: Commit**

Message: `♻️ Rename gh to gh-context for clarity`

---

## Task 2: Rename `gh-pr-comment-fixup` → `gh-pr-fixup`

**Files:**
- Rename: `skills/gh-pr-comment-fixup/` → `skills/gh-pr-fixup/`
- Modify: `skills/gh-pr-fixup/SKILL.md` (name field)
- Modify: `skills/gh-pr-respond/SKILL.md` (~8 references)
- Modify: `skills/gh-pr-triage/SKILL.md` (~4 references)
- Modify: `skills/git-fixup/SKILL.md` (~6 references)

**Step 1: Move directory**

```bash
git mv skills/gh-pr-comment-fixup skills/gh-pr-fixup
```

**Step 2: Update SKILL.md name field**

In `skills/gh-pr-fixup/SKILL.md`:
- `name: dx:gh-pr-comment-fixup` → `name: dx:gh-pr-fixup`
- Update any self-references in description/body

**Step 3: Update cross-references**

Replace all `dx:gh-pr-comment-fixup` → `dx:gh-pr-fixup` in:
- `skills/gh-pr-respond/SKILL.md` (description, dependencies list,
  workflow diagram, orchestration logic, batch mode, overall flow)
- `skills/gh-pr-triage/SKILL.md` (caller relationship, verdict
  handling, workflow diagram, delegation logic)
- `skills/git-fixup/SKILL.md` (called-by, return-to-caller,
  integration section, workflow)

Also replace any path references:
`~/.claude/skills/gh-pr-comment-fixup/` →
`~/.claude/skills/gh-pr-fixup/`

**Step 4: Verify no remaining references**

```bash
grep -r "comment-fixup" skills/ --include="*.md"
```

Expected: no matches

**Step 5: Commit**

Message: `♻️ Rename gh-pr-comment-fixup to gh-pr-fixup`

---

## Task 3: Rename `git-branch-groom` → `git-groom`

**Files:**
- Rename: `skills/git-branch-groom/` → `skills/git-groom/`
- Modify: `skills/git-groom/SKILL.md` (name + script paths)

**Step 1: Move directory**

```bash
git mv skills/git-branch-groom skills/git-groom
```

**Step 2: Update SKILL.md**

In `skills/git-groom/SKILL.md`:
- `name: dx:git-branch-groom` → `name: dx:git-groom`
- All `~/.claude/skills/git-branch-groom/` →
  `~/.claude/skills/git-groom/`
- All `Bash(~/.claude/skills/git-branch-groom/` →
  `Bash(~/.claude/skills/git-groom/`

**Step 3: Verify no remaining references**

```bash
grep -r "git-branch-groom" skills/ --include="*.md"
```

Expected: no matches

**Step 4: Commit**

Message: `♻️ Rename git-branch-groom to git-groom`

---

## Task 4: Rename `ticket-from-commit` → `git-promote`

**Files:**
- Rename: `skills/ticket-from-commit/` → `skills/git-promote/`
- Modify: `skills/git-promote/SKILL.md` (name + description +
  self-references)
- Modify: `skills/git-commit/SKILL.md` (reference to old skill)

**Step 1: Move directory**

```bash
git mv skills/ticket-from-commit skills/git-promote
```

**Step 2: Update SKILL.md**

In `skills/git-promote/SKILL.md`:
- `name: dx:ticket:from-commit` → `name: dx:git-promote`
- Update description to reflect new name
- Update any self-references in body

**Step 3: Update cross-references**

In `skills/git-commit/SKILL.md`:
- Replace `dx:ticket:from-commit` → `dx:git-promote`

**Step 4: Verify no remaining references**

```bash
grep -r "ticket.from.commit" skills/ --include="*.md"
grep -r "ticket-from-commit" skills/ --include="*.md"
```

Expected: no matches

**Step 5: Commit**

Message: `♻️ Rename ticket-from-commit to git-promote`

---

## Task 5: Rename park family (4 skills)

Rename all four park skills in one commit since they form a
cohesive family and cross-reference each other heavily.

**Files:**
- Rename: `skills/tasks-defer/` → `skills/park/`
- Rename: `skills/tasks-todo/` → `skills/park-todo/`
- Rename: `skills/tasks-remind/` → `skills/park-remind/`
- Rename: `skills/tasks-discover/` → `skills/park-discover/`
- Modify: all four SKILL.md files (name fields)
- Modify: `skills/gh-pr-bookmark/SKILL.md` (dx:defer refs)
- Modify: `skills/session-tasks/SKILL.md` (if already renamed) or
  `skills/tasks/SKILL.md` (dx:defer, dx:todo refs)
- Modify: `skills/session-wrap-up/SKILL.md` (if already renamed) or
  `skills/tasks-wrap-up/SKILL.md` (dx:defer, dx:todo, dx:discover refs)
- Modify: `skills/skill-motd/dependencies.txt` or
  `skills/skill-index/dependencies.txt`

**Step 1: Move directories**

```bash
git mv skills/tasks-defer skills/park
git mv skills/tasks-todo skills/park-todo
git mv skills/tasks-remind skills/park-remind
git mv skills/tasks-discover skills/park-discover
```

**Step 2: Update name fields in each SKILL.md**

- `skills/park/SKILL.md`: `name: dx:defer` → `name: dx:park`
- `skills/park-todo/SKILL.md`: `name: dx:todo` → `name: dx:park-todo`
- `skills/park-remind/SKILL.md`: `name: dx:remind` →
  `name: dx:park-remind`
- `skills/park-discover/SKILL.md`: `name: dx:discover` →
  `name: dx:park-discover`

**Step 3: Update invocation references in each SKILL.md body**

Within each park skill, update all references to siblings:
- `dx:defer` → `dx:park`
- `dx:todo` → `dx:park-todo`
- `dx:remind` → `dx:park-remind`
- `dx:discover` → `dx:park-discover`

Also update path references:
- `~/.claude/skills/tasks-defer/` → `~/.claude/skills/park/`
- `~/.claude/skills/tasks-todo/` → `~/.claude/skills/park-todo/`
- `~/.claude/skills/tasks-remind/` → `~/.claude/skills/park-remind/`
- `~/.claude/skills/tasks-discover/` →
  `~/.claude/skills/park-discover/`

**Step 4: Update cross-references in other skills**

- `skills/gh-pr-bookmark/SKILL.md`: all `dx:defer` → `dx:park`
- `skills/tasks/SKILL.md` or `skills/session-tasks/SKILL.md`:
  `dx:defer` → `dx:park`, `dx:todo` → `dx:park-todo`
- `skills/tasks-wrap-up/SKILL.md` or `skills/session-wrap-up/SKILL.md`:
  `dx:defer` → `dx:park`, `dx:todo` → `dx:park-todo`,
  `dx:discover` → `dx:park-discover`

**Step 5: Update dependency tracking**

In `dependencies.txt` (under skill-motd or skill-index):
- `dx:defer|dx:tasks,dx:todo,dx:remind` →
  `dx:park|dx:session-tasks,dx:park-todo,dx:park-remind`
- `dx:todo|dx:defer,dx:todo-review` →
  `dx:park-todo|dx:park,dx:todo-review`

**Step 6: Verify no remaining references**

```bash
grep -rw "dx:defer" skills/ --include="*.md"
grep -rw "dx:todo" skills/ --include="*.md"
grep -rw "dx:remind" skills/ --include="*.md"
grep -rw "dx:discover" skills/ --include="*.md"
grep -r "tasks-defer" skills/ --include="*.md"
grep -r "tasks-todo" skills/ --include="*.md"
grep -r "tasks-remind" skills/ --include="*.md"
grep -r "tasks-discover" skills/ --include="*.md"
```

Expected: no matches (only new names)

**Step 7: Commit**

Message: `♻️ Rename tasks deferral family to park`

---

## Task 6: Rename session family (2 skills)

**Files:**
- Rename: `skills/tasks/` → `skills/session-tasks/`
- Rename: `skills/tasks-wrap-up/` → `skills/session-wrap-up/`
- Modify: both SKILL.md files (name fields)
- Modify: park family skills that reference dx:tasks or dx:wrap-up

**Step 1: Move directories**

```bash
git mv skills/tasks skills/session-tasks
git mv skills/tasks-wrap-up skills/session-wrap-up
```

**Step 2: Update name fields**

- `skills/session-tasks/SKILL.md`:
  `name: dx:tasks` → `name: dx:session-tasks`
- `skills/session-wrap-up/SKILL.md`:
  `name: dx:wrap-up` stays as `name: dx:wrap-up` (invoke unchanged)

**Step 3: Update invocation references**

Replace `dx:tasks` → `dx:session-tasks` in:
- `skills/session-wrap-up/SKILL.md`
- `skills/park/SKILL.md` (if already renamed) or
  `skills/tasks-defer/SKILL.md`
- `dependencies.txt`

Replace path references:
- `~/.claude/skills/tasks/` → `~/.claude/skills/session-tasks/`
- `~/.claude/skills/tasks-wrap-up/` →
  `~/.claude/skills/session-wrap-up/`

**Step 4: Update dependency tracking**

In `dependencies.txt`:
- `dx:wrap-up|dx:tasks,dx:defer,dx:todo` →
  `dx:wrap-up|dx:session-tasks,dx:park,dx:park-todo`

**Step 5: Verify no remaining references**

```bash
grep -rw "dx:tasks[^-]" skills/ --include="*.md"
grep -r "skills/tasks/" skills/ --include="*.md"
grep -r "skills/tasks-wrap-up" skills/ --include="*.md"
```

Expected: no matches for old names

**Step 6: Commit**

Message: `♻️ Rename tasks lifecycle family to session`

---

## Task 7: Rename `skill-motd` → `skill-index`

**Files:**
- Rename: `skills/skill-motd/` → `skills/skill-index/`
- Modify: `skills/skill-index/SKILL.md` (name + script paths)
- Modify: `skills/skill-create/SKILL.md` (references to skill-motd)

**Step 1: Move directory**

```bash
git mv skills/skill-motd skills/skill-index
```

**Step 2: Update SKILL.md**

In `skills/skill-index/SKILL.md`:
- `name: dx:skill-motd` → `name: dx:skill-index`
- All `~/.claude/skills/skill-motd/` →
  `~/.claude/skills/skill-index/`

**Step 3: Update cross-references**

In `skills/skill-create/SKILL.md`:
- `skill-motd/scripts/generate-motd.sh` →
  `skill-index/scripts/generate-motd.sh`
- Any references to `dx:skill-motd` → `dx:skill-index`

**Step 4: Verify no remaining references**

```bash
grep -r "skill-motd" skills/ --include="*.md"
grep -r "skill-motd" skills/ --include="*.txt"
```

Expected: no matches

**Step 5: Commit**

Message: `♻️ Rename skill-motd to skill-index`

---

## Task 8: Update rules and documentation

**Files:**
- Modify: `.claude/rules/skill-naming.md`
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `.claude-plugin/plugin.json` (keywords if needed)

**Step 1: Update skill-naming.md**

Rewrite the "Abbreviated Names" section to reflect the new families:

```markdown
## Family Naming

Skills use family prefixes for tab-completion discoverability:

| Directory        | Invocation name     |
|------------------|---------------------|
| `park/`          | `dx:park`           |
| `park-todo/`     | `dx:park-todo`      |
| `park-remind/`   | `dx:park-remind`    |
| `park-discover/` | `dx:park-discover`  |
| `session-tasks/` | `dx:session-tasks`  |
| `session-wrap-up/`| `dx:wrap-up`       |
```

Update examples in "Good" sections to use new names.

**Step 2: Update README.md**

- Line 26-28: Update `/dx:tasks` → `/dx:session-tasks`,
  `/dx:defer` → `/dx:park`, task tracking section text
- Line 37: `/commit:to-new-ticket` → `/dx:git-promote`
- Line 46: Tasks family row — update all invocation names
- Line 112: `/dx:skill-motd` → `/dx:skill-index`

**Step 3: Update CLAUDE.md if it has skill references**

Check for any stale skill names and update.

**Step 4: Verify no stale references in docs**

```bash
grep -r "dx:defer\b" . --include="*.md" | grep -v plans/
grep -r "dx:todo\b" . --include="*.md" | grep -v plans/
grep -r "dx:tasks\b" . --include="*.md" | grep -v plans/
grep -r "skill-motd" . --include="*.md" | grep -v plans/
grep -r "ticket.from.commit" . --include="*.md" | grep -v plans/
grep -r "comment-fixup" . --include="*.md" | grep -v plans/
grep -r "git-branch-groom" . --include="*.md" | grep -v plans/
```

Expected: no matches outside `docs/plans/`

**Step 5: Commit**

Message: `📝 Update rules and docs for new skill names`

---

## Task 9: Final verification

**Step 1: Run skill-index to regenerate MOTD**

```bash
~/.claude/skills/skill-index/scripts/generate-motd.sh --force
```

Verify all new names appear in the generated index.

**Step 2: Full stale-reference scan**

```bash
grep -rE "dx:(gh[^-]|defer|todo[^-]|remind|discover|tasks[^-]|skill-motd|git-branch-groom|ticket)" skills/ .claude/ README.md CLAUDE.md --include="*.md" --include="*.txt" --include="*.sh" | grep -v "plans/"
```

Expected: no matches for old names.

**Step 3: Verify plugin loads**

```bash
claude plugin validate .
```

**Step 4: Commit any final fixes**

Message: `🩹 Fix remaining stale skill references`

---

## Ordering

Tasks 1-4 are independent (different families) and can run in
parallel or any order. Tasks 5-6 should run in sequence (session
family references park names). Task 7 is independent. Task 8
depends on all renames being complete. Task 9 is final verification.

```
Tasks 1-4 (parallel) → Task 5 → Task 6 → Task 7 → Task 8 → Task 9
```
