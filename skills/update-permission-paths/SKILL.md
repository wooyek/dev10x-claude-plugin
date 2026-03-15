---
name: dev10x:update-permission-paths
description: Use when the dev10x plugin version changes, or when worktree permissions need merging back — so all projects stay in sync instead of drifting one session at a time
user-invocable: true
invocation-name: update-permission-paths
allowed-tools:
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/update-permission-paths/scripts/*:*)
---

# Update Permission Paths

**Announce:** "Using update-permission-paths to update plugin version
references across all project settings."

## When to Use

- After installing a new dev10x plugin version
- When `Bash()` allow rules fail because paths reference an old version
- After `claude plugin update`
- When worktree sessions accumulate useful permissions the main project lacks

## First-Time Setup

Initialize userspace config with your project roots:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/update-permission-paths/scripts/update-paths.py --init
```

Then edit `~/.claude/skills/dev10x:update-permission-paths/projects.yaml`
to add your project roots.

## Workflow

1. Dry run first to preview changes:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/update-permission-paths/scripts/update-paths.py --dry-run
```

2. Apply updates:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/update-permission-paths/scripts/update-paths.py
```

## Configuration

The script looks for `projects.yaml` in two locations (first wins):
1. `~/.claude/skills/dev10x:update-permission-paths/projects.yaml` (userspace)
2. `${CLAUDE_PLUGIN_ROOT}/skills/update-permission-paths/projects.yaml` (plugin default)

The userspace config is user-specific and not tracked in git.
The plugin default ships with empty roots as a template.

## Merge Worktree Permissions

Worktrees accumulate allow rules during sessions that the main project
never sees. This script collects stable permissions from all worktrees
and merges them back.

1. Dry run to preview:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/update-permission-paths/scripts/merge-worktree-permissions.py --dry-run
```

2. Apply merge:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/update-permission-paths/scripts/merge-worktree-permissions.py
```

Session-specific noise (temp file hashes, inline conditionals, ticket-
specific script args) is filtered out automatically. Only stable,
reusable permissions are merged.

## Options

### update-paths.py

| Flag | Purpose |
|------|---------|
| `--dry-run` | Preview changes without writing |
| `--version X.Y.Z` | Target a specific version instead of latest |
| `--init` | Copy plugin default config to userspace for customization |

### merge-worktree-permissions.py

| Flag | Purpose |
|------|---------|
| `--dry-run` | Preview what would be merged without writing |
