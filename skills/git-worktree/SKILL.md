---
name: dx:git-worktree
description: >
  Create git worktrees outside the project directory for clean IDE isolation.
  Handles post-checkout hook setup, next-number naming, and SessionEnd cleanup prompt.
user-invocable: true
invocation-name: dx:git-worktree
allowed-tools:
  - Bash(~/.claude/skills/git-worktree/scripts/*:*)
  - Bash(git worktree list:*)
  - Bash(git worktree remove:*)
---

# Git Worktree — External Isolation

Create worktrees **outside** the project directory to prevent IDE cross-indexing
and accidental imports between worktrees.

**Announce:** "Using dx:git-worktree skill to create an isolated workspace."

## Why Outside the Project?

Worktrees inside the project (`.worktrees/`, `.claude/worktrees/`) cause:
- IDEs indexing files from sibling worktrees
- Accidental imports resolving to wrong worktree
- Cluttered project root

## Workflow

### Step 1: Determine Worktree Location

Default pattern: `../.worktrees/<project-basename>-NN`

Example for `/work/myproject/myproject`: `/work/myproject/.worktrees/myproject-1`

Check user memory for a preferred location override. If found, use it.

Calculate next number:

```bash
~/.claude/skills/git-worktree/scripts/next-worktree-name.sh
```

This prints the full path for the next available worktree.

### Step 2: Confirm with User

Ask the user to confirm the worktree path and which branch to base it on
(default: current HEAD). Use AskUserQuestion with options:

- **Create at `<calculated-path>`** (Recommended)
- **Custom location** — let user specify

### Step 3: Check post-checkout Hook

Read `.git/hooks/post-checkout` (or `.husky/post-checkout`) if it exists.
If it already handles worktree setup adequately, skip to Step 4.

**Important:** The skill does NOT run setup commands directly.
The `post-checkout` hook is responsible for all environment setup.

If the hook is **missing or incomplete**, detect the project type and propose
the appropriate template (see below). Present to the user for approval before
writing.

#### All hooks: use the all-zeros SHA guard

Always use the all-zeros SHA to detect new worktree creation — this is what
`git worktree add` passes as `$1` (previous HEAD). Do NOT use `[ -f .git ]`
which would trigger on every branch checkout inside any existing worktree:

```sh
if [ "$1" = "0000000000000000000000000000000000000000" ]; then
    # new worktree — run setup
fi
```

#### Step 3a: Detect project type

Check these files to determine which template to use:

| Check | Meaning |
|---|---|
| `uv.lock` or `pyproject.toml` exists | **Python/uv** project |
| `package.json` exists | **Node.js** project |
| `.husky/` directory exists **or** `package.json` contains `"prepare": "husky"` | Node.js **with Husky** |
| `package.json` has a top-level `"workspaces"` key | Node.js **monorepo** (yarn/npm workspaces) |
| Multiple `package.json` files in subdirs + root `package.json` | **Monorepo** — run install from root |

A project can be Python-only, Node.js-only, or both (e.g., Django + React
frontend in the same repo). Apply all matching templates.

#### Step 3b: Determine hook file location

| Condition | Write to |
|---|---|
| `.husky/` directory exists or Husky in `prepare` script | **`.husky/post-checkout`** (tracked in git) |
| No Husky | **`.git/hooks/post-checkout`** (untracked, local only) |

**Why:** Husky manages `.git/hooks/` and overwrites it whenever
`yarn install` / `npm install` runs the `prepare` script. Writing to
`.git/hooks/post-checkout` in a Husky project means your changes are silently
lost on next install. `.husky/post-checkout` is tracked in git and survives
re-installs.

#### Template A: Python/uv project

```sh
#!/bin/sh

if [ "$1" = "0000000000000000000000000000000000000000" ]; then
    echo "New worktree detected. Running setup..."
    pwd

    ORIGINAL_REPO=/work/<project-name>

    cp "$ORIGINAL_REPO/.env" . 2>/dev/null || echo "No .env found to copy."
    cp "$ORIGINAL_REPO/development.secrets.env" . \
        2>/dev/null || echo "No development.secrets.env found to copy."
    cp -r "$ORIGINAL_REPO/.claude" . 2>/dev/null || echo "No .claude found to copy."
    cp -r "$ORIGINAL_REPO/.idea" . 2>/dev/null || echo "No .idea found to copy."

    if command -v uv >/dev/null; then
        echo "Running uv sync..."
        uv sync
    fi
fi
```

Adjust which files to copy based on what actually exists in the project root
(check `git status --short` for untracked files in the original repo).

#### Template B: Node.js + Husky (write to `.husky/post-checkout`)

```sh
#!/bin/sh

if [ "$1" = "0000000000000000000000000000000000000000" ]; then
    echo "New worktree detected. Running setup..."
    pwd

    ORIGINAL_REPO=/work/<project-name>

    cp "$ORIGINAL_REPO/.env" . 2>/dev/null || echo "No .env found to copy."
    cp -r "$ORIGINAL_REPO/.claude" . 2>/dev/null || echo "No .claude found to copy."

    if command -v yarn >/dev/null; then
        echo "Running yarn install..."
        yarn install --frozen-lockfile
    fi
fi
```

For **monorepos** (yarn workspaces), run `yarn install --frozen-lockfile` from
the repo root — this installs all workspace packages in one pass.

#### Template C: Node.js without Husky (write to `.git/hooks/post-checkout`)

```sh
#!/bin/sh

if [ "$1" = "0000000000000000000000000000000000000000" ]; then
    echo "New worktree detected. Running setup..."
    pwd

    ORIGINAL_REPO=/work/<project-name>

    cp "$ORIGINAL_REPO/.env" . 2>/dev/null || echo "No .env found to copy."
    cp -r "$ORIGINAL_REPO/.claude" . 2>/dev/null || echo "No .claude found to copy."

    if command -v yarn >/dev/null; then
        yarn install --frozen-lockfile
    elif command -v npm >/dev/null; then
        npm ci
    fi
fi
```

Make the file executable: `chmod +x .git/hooks/post-checkout`

#### Node.js: never symlink node_modules

Do **not** use `ln -sfn .../node_modules node_modules`. A symlink means
`yarn add` / `yarn remove` in any worktree mutates the shared directory,
breaking isolation across all worktrees. Always run
`yarn install --frozen-lockfile` to give each worktree its own copy.
Yarn's global cache makes this fast (hardlinks from `~/.yarn/cache`).

### Step 4: Create the Worktree

Use the script to wrap the command — this keeps it under a pre-approved path
so permission prompts are not triggered by the long `git -C ... worktree add`
form:

```bash
~/.claude/skills/git-worktree/scripts/create-worktree.sh \
  <worktree-path> <branch-name> [repo-root]
```

- `repo-root` is required when the current working directory differs from the
  target repo (e.g. creating a worktree for one project while in another).
- Omit `repo-root` when already inside the target repo.

Examples:

```bash
# From inside the target repo
~/.claude/skills/git-worktree/scripts/create-worktree.sh \
  /work/myproject/.worktrees/myproject-1 user/TICKET-123/feature-description

# From a different directory (repo-root required)
~/.claude/skills/git-worktree/scripts/create-worktree.sh \
  /work/myproject/.worktrees/myproject-1 user/TICKET-123/feature-description \
  /work/myproject/myproject
```

The branch name should follow project conventions (e.g., from ticket:branch skill).
If no branch name is provided, ask the user or use a descriptive name.

The `post-checkout` hook fires automatically after the script runs.

### Step 5: Install SessionEnd Cleanup Hook

Run the setup script to configure a SessionEnd hook in the new worktree
that will prompt the user to remove the worktree when the session ends:

```bash
~/.claude/skills/git-worktree/scripts/setup-session-end-hook.sh <worktree-path>
```

This creates/updates `<worktree-path>/.claude/settings.local.json` with a
SessionEnd hook pointing to the cleanup prompt script.

### Step 6: Report

Print:
- Worktree path
- Branch name
- Whether post-checkout hook ran successfully
- Reminder: `cd <path>` to start working, or open in a new IDE window

## Cleanup

The SessionEnd hook in the worktree prompts the user:

> This session used worktree at `<path>`. Remove it? [y/N]

If yes, runs `git worktree remove <path>`.
If no or timeout, the worktree persists for future sessions.

To manually remove:

```bash
git worktree remove <path>
# or force if dirty:
git worktree remove --force <path>
```

To list all worktrees:

```bash
git worktree list
```
