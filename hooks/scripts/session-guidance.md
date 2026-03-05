# Session Guidance — Patterns & Anti-Patterns

Quick reference for every session. Hooks enforce most of these
rules automatically; this briefing explains **why** so you choose
the right pattern on the first attempt.

## Hook-Blocked Patterns (enforced)

| Pattern | Why blocked | Use instead |
|---------|------------|-------------|
| `cmd1 && cmd2` (setup + path-based script) | `&&` shifts prefix, breaks allow rules for path-based commands | Separate Bash tool calls |
| `cat <<'EOF'` / `cat >` / `echo >` | Heredocs/redirects blocked by security hook | Write tool + reference file (`git commit -F`) |
| `python3 -c "..."` inline code | Inline execution blocked | Extract to `~/.claude/tools/script.py` with uv shebang |

## Permission-Friction Anti-Patterns (advisory)

These are not always hook-blocked, but they commonly trigger avoidable
prompts or brittle command matching.

| Pattern | Why risky | Use instead |
|---------|-----------|-------------|
| `$(git merge-base ...)` inline | Subshell shifts effective command prefix | Git aliases: `git develop-log`, `git develop-diff`, `git develop-rebase` |
| `# comment` as first line | Leading `#` can break prefix matching and parser expectations | Use Bash tool `description` parameter |
| `ENV=val command` prefix | Env prefix can shift the effective prefix used for allow rules | Script sets env internally |
| `uv run --script` on executable scripts | Redundant wrapper can miss direct path-based allow rules | Call script directly (shebang handles uv) |
| `cd /worktree/path && command` | Redundant when CWD is already the worktree; can trigger chaining checks | Run command directly — session switched on worktree creation |

## Preferred Patterns

### Git operations
- `git develop-log` — commits since diverging from develop
- `git develop-diff` — diff since diverging from develop
- `git develop-rebase` — interactive rebase onto develop
- If aliases are missing, run `/dev10x:git-alias-setup`

### Multiline content (commit messages, PR bodies)
1. Write content to a temp file via Write tool
2. Reference: `git commit -F /tmp/file.txt` or `gh pr create --body-file /tmp/file.txt`

### Staging and committing
- **Never** chain: `git add && git commit`
- Use two separate Bash tool calls

### Commit messages
- JTBD outcome-focused: "Enable X" not "Add X"
- Gitmoji prefix + ticket ID: `♻️ PAY-32 Enable multi-location routing`
- Max 72 characters per line
- Hook validates verb choice automatically

### Script invocation
- Scripts in `~/.claude/skills/` and `~/.claude/tools/` are self-executing
- Call directly: `~/.claude/tools/script.py args`
- Never prefix with `uv run --script` — the shebang handles it

### Worktrees
- When a worktree is created via `/dev10x:git-worktree`, the session
  CWD switches to it automatically — no `cd` needed
- If CWD is already a worktree (`.git` is a file), do not
  `cd` into it before running commands — you are already there
- Check with `git rev-parse --show-toplevel` if unsure

### Temporary files
- Use `/tmp/claude/bin/mktmp.sh <namespace> <prefix> [.ext]`
- This stable `/tmp` path is installed at SessionStart to avoid
  plugin-cache/version path permission friction
- Never `mkdir -p && script` — `mktmp.sh` creates dirs automatically
- Keep it as a standalone Bash call (no `&&` prefix setup)

## Key Skills for Common Tasks

| Task | Skill |
|------|-------|
| Create commit | `/dev10x:git-commit` |
| Create PR | `/dev10x:gh-pr-create` |
| Review PR | `/dev10x:gh-pr-review` |
| Respond to PR review | `/dev10x:gh-pr-respond` |
| Create branch from ticket | `/dev10x:ticket-branch` |
| Create worktree | `/dev10x:git-worktree` |
| Groom commits before merge | `/dev10x:git-groom` |
| Push safely | `/dev10x:git` (validates protected branches) |
| Audit this session | `/dev10x:skill-audit` |
