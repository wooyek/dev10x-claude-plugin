# dev10x Claude Plugin

Stop babysitting your AI. Start supervising it.

---

A Claude Code plugin that gives your AI pre-approved workflows,
self-correcting guardrails, and a complete scope-to-merge pipeline —
so you can supervise in 5-minute windows instead of hovering over
every command.

## The problem with AI coding assistants

**Permission friction kills autonomy.** Every ad-hoc bash command
triggers a permission prompt. Every prompt pulls you back to the
terminal. Your AI can write code, but it can't ship a commit
without asking you 15 times.

**Progress is invisible.** You walk away for 10 minutes and come
back to a wall of terminal output. Or a stalled session waiting
for approval. No way to tell at a glance if things are on track.

**Attention doesn't batch.** You want to give 5 minutes of
direction, check in during coffee, and move on. Instead you're
hovering — approving every shell command, every file write, every
git operation.

## How dev10x solves this

### Pre-approved workflows, not ad-hoc scripts

40 skills encapsulate complete dev workflows as slash commands.
`/commit` handles gitmoji, ticket reference, and benefit-focused
title — all through pre-approved tool calls that never trigger
permission prompts.

When Claude uses `/dev10x:gh-pr-create` instead of raw `gh` commands, every
step matches an allow rule. Zero interruptions.

### Guardrails that teach, not just block

8 hooks intercept dangerous patterns *before* they execute — and
redirect the AI toward the approved path:

- **`detect-and-chaining`** catches `mkdir && script.sh` that
  breaks allow rules → teaches separate calls
- **`block-python3-inline`** blocks `python3 -c "..."` →
  teaches `uv run --script`
- **`validate-commit-jtbd`** blocks "Add retry logic" → teaches
  "Enable automatic retry on failure"

The hooks carry educational messages. The AI learns from each
block. By mid-session, it stops triggering them entirely.

### A complete scope-to-merge pipeline

Every step produces a precise, artifact-quality message — readable
by the next agent in the chain or a human reviewer glancing at
their phone:

| Step | Skill | Output |
|------|-------|--------|
| Scope | `dev10x:ticket-scope` | Architecture research, ticket update |
| Branch | `dev10x:work-on` | Named branch, gathered context |
| Commit | `dev10x:git-commit` | Atomic commits with benefit-focused titles |
| Groom | `dev10x:git-groom` | Clean history, no fixup commits |
| PR | `dev10x:gh-pr-create` | Job Story description, ticket links |
| Monitor | `dev10x:gh-pr-monitor` | Background CI + review watch |
| Respond | `dev10x:gh-pr-respond` | Batched review responses, minimal noise |
| Review | `dev10x:gh-pr-review` | Domain-routed review across 5 agents |

No step produces wall-of-text. Each output is sized for a Slack
preview, a PR comment, or a task list glance.

### Learning loops that calibrate to you

Code review findings, commit conventions, and PR feedback flow
back into CLAUDE.md rules and session memory. The more you
course-correct, the less you need to.

After a few sessions, the AI produces commits, PR descriptions,
and code that look like *you* wrote them — because it learned your
preferences, not generic defaults.

## Supervise, don't babysit

The plugin is designed around batched attention windows:

1. **Scope** — point at a ticket, let the AI research and plan
2. **Walk away** — skills and hooks keep the pipeline moving
3. **Check in** — task list shows where the session stands
4. **Course-correct** — give 2 minutes of guidance, walk away again
5. **Ship** — come back to a groomed branch, clean PR, ready for
   review

When you pop in during a coffee break, you see a task list — not
a wall of terminal output. Each artifact (commit message, PR body,
review comment) is concise enough to evaluate in seconds.

## Skill families

| Family | Skills | What it automates |
|--------|--------|-------------------|
| **Git** (8) | `git-commit`, `git-commit-split`, `git-fixup`, `git-groom`, `git-promote`, `git-worktree`, `git`, `git-alias-setup` | Atomic commits, clean history, workspace isolation |
| **PR** (9) | `gh-pr-create`, `gh-pr-review`, `gh-pr-respond`, `gh-pr-monitor`, `gh-pr-triage`, `gh-pr-fixup`, `gh-pr-request-review`, `gh-pr-bookmark`, `gh-context` | Full PR lifecycle, domain-routed review |
| **Tickets** (6) | `ticket-create`, `ticket-branch`, `ticket-scope`, `ticket-jtbd`, `work-on`, `linear` | Issue tracker integration, ticket scoping |
| **Park** (4) | `park`, `park-todo`, `park-remind`, `park-discover` | Deferred work parking |
| **Scoping** (3) | `scope`, `jtbd`, `adr` | Architecture decisions, Job Story format |
| **QA** (3) | `qa-scope`, `qa-self`, `playwright` | Test planning, self-review, browser testing |
| **Session** (2) | `session-tasks`, `wrap-up` | In-session work tracking |
| **Tooling** (2) | `py-uv`, `slack` | Python packaging, Slack notifications |
| **Meta** (3) | `skill-create`, `skill-audit`, `skill-index` | Create, audit, and discover skills |

All skills use the `dev10x:` prefix — type `/dev10x:git-commit` in the Claude
Code CLI to run it. Run `/dev10x:skill-index` for the full reference.

## Installation

### Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
  installed and authenticated
- Git 2.20+ (for worktree support)
- GitHub CLI (`gh`) installed and authenticated

### Option A: Marketplace install (recommended)

Add the marketplace source and install the plugin:

```
/plugin marketplace add wooyek/dev10x-claude-plugin
/plugin install dev10x@dev10x
```

Update to the latest version:

```
/plugin update dev10x@dev10x
```

### Option B: Manual clone

This is a private repository. You need GitHub access granted through
the [Dev10x community](https://www.skool.com/dev10x-1892). Once you
have access:

```bash
git clone git@github.com:wooyek/dev10x-claude-plugin.git \
  ~/.claude/plugins/dev10x-claude-plugin
```

> **Using HTTPS?** Replace the URL with
> `https://github.com/wooyek/dev10x-claude-plugin.git` and
> authenticate when prompted.

Register the plugin so Claude Code loads it on every session:

```bash
claude plugin add --local ~/.claude/plugins/dev10x-claude-plugin
```

Update manually with:

```bash
cd ~/.claude/plugins/dev10x-claude-plugin && git pull
```

### Verify the installation

Start a new Claude Code session and check that skills are loaded:

```bash
claude
# Inside the session, type:
/dev10x:skill-index
```

You should see a skills reference listing all available commands.

### Try without installing

Load the plugin for a single session:

```bash
claude --plugin-dir ~/.claude/plugins/dev10x-claude-plugin
```

## Getting access

This plugin is available to members of the
[Dev10x community on Skool](https://www.skool.com/dev10x-1892).
To get access:

1. Join the community at https://www.skool.com/dev10x-1892
2. Share your GitHub username in the community
3. You will be added as a collaborator to the private repo
4. Clone and install using the steps above

## Development

Test locally without installing:

```bash
claude --plugin-dir /path/to/dev10x-claude-plugin
```

Validate plugin structure:

```bash
claude plugin validate /path/to/dev10x-claude-plugin
```

## License

MIT
