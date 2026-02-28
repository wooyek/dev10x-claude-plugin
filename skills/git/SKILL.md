---
name: dx:git
description: Use before running git push or git rebase — so force-pushes to
  protected branches are blocked and non-interactive rebases run unattended
  without manual editor approval prompts.
user-invocable: true
invocation-name: dx:git
allowed-tools:
  - Bash(~/.claude/skills/git/scripts/git-push-safe.sh:*)
  - Bash(~/.claude/skills/git/scripts/git-rebase-groom.sh:*)
  - Bash(~/.claude/skills/git/scripts/git-seq-editor.sh:*)
  - Bash(git reset --soft:*)
  - Bash(git push --force-with-lease:*)
  - Write(/tmp/claude/branch-groom/**)
---

**Announce:** "Using dx:git to [push / groom commits]."

# dx:git — Hardened Git Operations

Provides hardened scripts for safe git push and non-interactive rebase.
Add the `allowed-tools` entries to your project's `settings.local.json`
to pre-approve the scripts without per-call prompts.

## Safe Push

Always push via the wrapper script to prevent force-pushing to protected
branches:

```bash
~/.claude/skills/git/scripts/git-push-safe.sh [git push arguments...]
```

Default protected branches: `main master`

To extend the list, set `GIT_PROTECTED_BRANCHES` before calling:

```bash
GIT_PROTECTED_BRANCHES="main master staging" \
  ~/.claude/skills/git/scripts/git-push-safe.sh --force-with-lease
```

`--force-with-lease` is always allowed (verifies the remote has not
diverged before overwriting). `--force` and `-f` are blocked on
protected branches.

## Non-Interactive Rebase

Two scripts power fully automated rebases:

- **`git-seq-editor.sh`** — replaces `GIT_SEQUENCE_EDITOR`; reads the
  rebase todo sequence from `/tmp/claude/branch-groom/rebase-seq.txt` and
  injects it into the rebase todo file.
- **`git-rebase-groom.sh`** — convenience wrapper that sets
  `GIT_SEQUENCE_EDITOR` and `GIT_EDITOR=true`, then runs
  `git rebase -i <base-ref>`.

### Usage

1. Write the rebase todo (oldest commit first) using the Write tool:

```
Write /tmp/claude/branch-groom/rebase-seq.txt:
pick abc1234 First commit
pick def5678 Second commit
fixup fed9876 fixup! Second commit
```

The `git-rebase-groom.sh` script creates `/tmp/claude/branch-groom/` automatically,
so no `mkdir` is needed before writing the file.

**Note:** The Write tool requires reading a file before writing to it.
For the first rebase in a session (when the file doesn't exist yet),
create it first:

```bash
touch /tmp/claude/branch-groom/rebase-seq.txt
```

Then Read the file, then Write the sequence content.

2. Run the rebase:

```bash
~/.claude/skills/git/scripts/git-rebase-groom.sh <base-ref>
```

### Sequence file ordering

The sequence file must list commits **oldest at the top, newest at the
bottom** — the same order `git rebase -i` expects. Use `tac` to
reverse `git log` output:

```bash
git log --oneline <base>..HEAD | tac
```

### SHA staleness

After each rebase pass all commit SHAs change. Always re-run
`git log --oneline <base>..HEAD` after each pass and use fresh SHAs
when writing the next sequence file.

## Branch Comparison Aliases

Use git aliases instead of embedding `$(git merge-base ...)` in
commands. The `$(...)` substitution creates compound commands that
break Claude Code permission prefix matching, causing unnecessary
permission prompts.

| Alias                | Equivalent                                                     |
|----------------------|----------------------------------------------------------------|
| `git develop-log`    | `git log --oneline $(git merge-base develop HEAD)..HEAD`       |
| `git develop-diff`   | `git diff $(git merge-base develop HEAD)..HEAD`                |
| `git develop-rebase` | `git rebase -i --autosquash $(git merge-base develop HEAD)`    |

The alias name includes the base branch. When a different base is
needed (e.g., `trunk`), add a parallel set: `trunk-log`, `trunk-diff`,
`trunk-rebase`.

**Never use `$(git merge-base ...)` inline** — always use the alias.

## settings.local.json wiring

Add to your project's `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(~/.claude/skills/git/scripts/git-push-safe.sh:*)",
      "Bash(~/.claude/skills/git/scripts/git-rebase-groom.sh:*)",
      "Bash(~/.claude/skills/git/scripts/git-seq-editor.sh:*)",
      "Bash(git reset --soft:*)",
      "Bash(git push --force-with-lease:*)",
      "Write(/tmp/claude/branch-groom/**)"
    ]
  }
}
```
