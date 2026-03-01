---
name: dx:git-worktree
description: >
  Create git worktrees for clean workspace isolation.
  Offers two modes: native EnterWorktree (switches CWD in current session)
  or external worktree (IDE-isolated, requires restarting claude in new dir).
user-invocable: true
invocation-name: dx:git-worktree
allowed-tools:
  - Bash(~/.claude/skills/git-worktree/scripts/*:*)
  - Bash(git worktree list:*)
  - Bash(git worktree remove:*)
---

# Git Worktree

**Announce:** "Using dx:git-worktree skill to create an isolated workspace."

## Workflow

### Step 1: Determine Branch Name

The branch name is needed by both paths. Follow project naming conventions:

- username: check `git branch -a` for the pattern used (e.g. `janusz`)
- slug: lowercase ticket title, hyphens, stop-words removed, max 3–4 words
- format: `username/TICKET-ID/slug`

### Step 2: Choose Worktree Mode

Present the two options with AskUserQuestion:

- **Same session** (Recommended) — native `EnterWorktree` tool switches CWD
  immediately; all subsequent git commands and skills (`commit`, `pr:create`,
  `branch:groom`) work without flags; worktree lives inside `.claude/worktrees/`
- **External + new session** — worktree created at `../.worktrees/<project>-NN`
  outside the project; IDE won't cross-index sibling worktrees; requires closing
  this session and opening a new one in the worktree directory

Continue to **Path A** or **Path B** based on the choice.

---

## Path A — Same Session (EnterWorktree)

### Step A1: Check post-checkout Hook

Read `.git/hooks/post-checkout` (or `.husky/post-checkout`) if it exists.
If it handles worktree setup adequately (uv sync, yarn install, env copy),
skip to Step A2.

If missing or incomplete, detect project type and propose the appropriate
template from the **Hook Templates** section below. Present to the user for
approval before writing.

### Step A2: Create Worktree (native tool)

Call the native `EnterWorktree` tool:
- `name`: use the branch slug (e.g. `fix-railway-deployment`)

After `EnterWorktree` runs the session CWD is the new worktree. All
subsequent Bash calls, git commands, and skills operate inside it.

### Step A3: Continue Workflow

The session is now in the worktree. Resume the calling skill's next step
(ticket status, job story, summary). No restart needed.

---

## Path B — External + New Session

### Step B1: Determine Worktree Location

Default pattern: `../.worktrees/<project-basename>-NN`

Calculate the next available path:

```bash
~/.claude/skills/git-worktree/scripts/next-worktree-name.sh
```

Ask user to confirm (AskUserQuestion):
- **Create at `<calculated-path>`** (Recommended)
- **Custom location** — let user specify

### Step B2: Check post-checkout Hook

Same as Step A1 — read, verify, and propose a template if needed.
See **Hook Templates** section below.

### Step B3: Create the Worktree

```bash
~/.claude/skills/git-worktree/scripts/create-worktree.sh \
  <worktree-path> <branch-name> [repo-root]
```

- Omit `repo-root` when already inside the target repo.
- Pass `repo-root` when the CWD differs from the target repo.

The `post-checkout` hook fires automatically after this script runs.

### Step B4: Install SessionEnd Cleanup Hook

```bash
~/.claude/skills/git-worktree/scripts/setup-session-end-hook.sh <worktree-path>
```

This writes a SessionEnd hook into `<worktree-path>/.claude/settings.local.json`
that prompts the user to remove the worktree when the new session ends.

### Step B5: Hand Off — STOP HERE

Claude Code sessions have a fixed CWD. `cd` inside a Bash call does not
persist, so every subsequent git command would need `git -C <path>` and
skills like `pr:create` (whose `verify-state.sh` runs plain `git`) would fail.

Print this message and **stop — do not continue with ticket workflow steps**:

```
✅ Worktree ready
   Path:   <worktree-path>
   Branch: <branch-name>

Close this session and open a new one in the worktree:

  cd <worktree-path> && claude

Copy the command above, close this session, then paste it in your terminal.
The new session will have the correct CWD and all skills will work normally.
```

---

## Hook Templates

Templates for projects that lack a `post-checkout` hook.

### All hooks: use the all-zeros SHA guard

`git worktree add` passes `0000000000000000000000000000000000000000` as `$1`
(previous HEAD) when creating a new worktree. Guard on this value — do NOT
use `[ -f .git ]` which fires on every branch checkout inside any worktree:

```sh
if [ "$1" = "0000000000000000000000000000000000000000" ]; then
    # new worktree — run setup
fi
```

### Detect project type

| Check | Template |
|---|---|
| `uv.lock` or `pyproject.toml` exists | Template A (Python/uv) |
| `package.json` + `.husky/` directory | Template B (Node + Husky) |
| `package.json` without Husky | Template C (Node, no Husky) |

A project can match multiple templates (e.g. Django + SvelteKit). Apply all.

### Hook file location

| Condition | Write to |
|---|---|
| Husky present (`prepare` script or `.husky/` dir) | `.husky/post-checkout` (tracked) |
| No Husky | `.git/hooks/post-checkout` (untracked, local only) |

Husky overwrites `.git/hooks/` on every `yarn/npm install`. Writing to
`.git/hooks/post-checkout` in a Husky project means changes are silently lost.

### Template A: Python/uv

```sh
#!/bin/sh
if [ "$1" = "0000000000000000000000000000000000000000" ]; then
    echo "New worktree detected. Running setup..."
    pwd
    ORIGINAL_REPO=/work/<org>/<project-name>
    cp "$ORIGINAL_REPO/.env" . 2>/dev/null || echo "No .env found."
    cp "$ORIGINAL_REPO/development.secrets.env" . 2>/dev/null || true
    cp -r "$ORIGINAL_REPO/.claude" . 2>/dev/null || true
    cp -r "$ORIGINAL_REPO/.idea" . 2>/dev/null || true
    command -v uv >/dev/null && uv sync
fi
```

### Template B: Node.js + Husky (write to `.husky/post-checkout`)

```sh
#!/bin/sh
if [ "$1" = "0000000000000000000000000000000000000000" ]; then
    echo "New worktree detected. Running setup..."
    pwd
    ORIGINAL_REPO=/work/<org>/<project-name>
    cp "$ORIGINAL_REPO/.env" . 2>/dev/null || echo "No .env found."
    cp -r "$ORIGINAL_REPO/.claude" . 2>/dev/null || true
    command -v yarn >/dev/null && yarn install --frozen-lockfile
fi
```

For monorepos (yarn workspaces), run `yarn install --frozen-lockfile` from
the repo root — this installs all workspace packages in one pass.

### Template C: Node.js without Husky (write to `.git/hooks/post-checkout`)

```sh
#!/bin/sh
if [ "$1" = "0000000000000000000000000000000000000000" ]; then
    echo "New worktree detected. Running setup..."
    pwd
    ORIGINAL_REPO=/work/<org>/<project-name>
    cp "$ORIGINAL_REPO/.env" . 2>/dev/null || echo "No .env found."
    cp -r "$ORIGINAL_REPO/.claude" . 2>/dev/null || true
    if command -v yarn >/dev/null; then
        yarn install --frozen-lockfile
    elif command -v npm >/dev/null; then
        npm ci
    fi
fi
```

Make executable: `chmod +x .git/hooks/post-checkout`

**Never symlink `node_modules`** — a symlink means `yarn add/remove` in any
worktree mutates the shared directory. Always run `yarn install --frozen-lockfile`
(fast via Yarn's hardlink cache).

---

## Cleanup

The SessionEnd hook installed by Path B prompts:

> This session used worktree at `<path>`. Remove it? [y/N]

If yes: `git worktree remove <path>`
If no: the worktree persists for future sessions.

Manual removal:

```bash
git worktree remove <path>
git worktree remove --force <path>  # if dirty
git worktree list                   # list all worktrees
```
