# Dev10x Claude Plugin

Stop babysitting your AI. Start supervising it.  
Join the community: https://www.skool.com/Dev10x-1892/about

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

## How Dev10x solves this

### Pre-approved workflows, not ad-hoc scripts

59 skills encapsulate complete dev workflows as slash commands.
`/commit` handles gitmoji, ticket reference, and benefit-focused
title — all through pre-approved tool calls that never trigger
permission prompts.

When Claude uses `/Dev10x:gh-pr-create` instead of raw `gh` commands, every
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
| Scope | [`Dev10x:ticket-scope`](skills/ticket-scope/SKILL.md) | Architecture research, ticket update |
| Branch | [`Dev10x:work-on`](skills/work-on/SKILL.md) | Named branch, gathered context |
| Commit | [`Dev10x:git-commit`](skills/git-commit/SKILL.md) | Atomic commits with benefit-focused titles |
| Groom | [`Dev10x:git-groom`](skills/git-groom/SKILL.md) | Clean history, no fixup commits |
| PR | [`Dev10x:gh-pr-create`](skills/gh-pr-create/SKILL.md) | Job Story description, ticket links |
| Monitor | [`Dev10x:gh-pr-monitor`](skills/gh-pr-monitor/SKILL.md) | Background CI + review watch |
| Respond | [`Dev10x:gh-pr-respond`](skills/gh-pr-respond/SKILL.md) | Batched review responses, minimal noise |
| Review | [`Dev10x:gh-pr-review`](skills/gh-pr-review/SKILL.md) | Domain-routed review across 5 agents |

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
| **Git** | [`git-commit`](skills/git-commit/SKILL.md), [`git-commit-split`](skills/git-commit-split/SKILL.md), [`git-fixup`](skills/git-fixup/SKILL.md), [`git-groom`](skills/git-groom/SKILL.md), [`git-promote`](skills/git-promote/SKILL.md), [`git-worktree`](skills/git-worktree/SKILL.md), [`git`](skills/git/SKILL.md), [`git-alias-setup`](skills/git-alias-setup/SKILL.md) | Atomic commits, clean history, workspace isolation |
| **PR** | [`gh-pr-create`](skills/gh-pr-create/SKILL.md), [`gh-pr-review`](skills/gh-pr-review/SKILL.md), [`gh-pr-respond`](skills/gh-pr-respond/SKILL.md), [`gh-pr-monitor`](skills/gh-pr-monitor/SKILL.md), [`gh-pr-triage`](skills/gh-pr-triage/SKILL.md), [`gh-pr-fixup`](skills/gh-pr-fixup/SKILL.md), [`gh-pr-request-review`](skills/gh-pr-request-review/SKILL.md), [`gh-pr-bookmark`](skills/gh-pr-bookmark/SKILL.md), [`gh-context`](skills/gh-context/SKILL.md), [`request-review`](skills/request-review/SKILL.md) | Full PR lifecycle, domain-routed review |
| **Tickets** | [`ticket-create`](skills/ticket-create/SKILL.md), [`ticket-branch`](skills/ticket-branch/SKILL.md), [`ticket-scope`](skills/ticket-scope/SKILL.md), [`ticket-jtbd`](skills/ticket-jtbd/SKILL.md), [`work-on`](skills/work-on/SKILL.md), [`linear`](skills/linear/SKILL.md), [`project-scope`](skills/project-scope/SKILL.md) | Issue tracker integration, ticket scoping |
| **Park** | [`park`](skills/park/SKILL.md), [`park-todo`](skills/park-todo/SKILL.md), [`park-remind`](skills/park-remind/SKILL.md), [`park-discover`](skills/park-discover/SKILL.md) | Deferred work parking |
| **Scoping** | [`scope`](skills/scope/SKILL.md), [`jtbd`](skills/jtbd/SKILL.md), [`adr`](skills/adr/SKILL.md) | Architecture decisions, Job Story format |
| **QA** | [`qa-scope`](skills/qa-scope/SKILL.md), [`qa-self`](skills/qa-self/SKILL.md), [`playwright`](skills/playwright/SKILL.md) | Test planning, self-review, browser testing |
| **Session** | [`session-tasks`](skills/session-tasks/SKILL.md), [`session-wrap-up`](skills/session-wrap-up/SKILL.md) | In-session work tracking |
| **DB** | [`db`](skills/db/SKILL.md), [`db-psql`](skills/db-psql/SKILL.md) | Safe database query planning and execution |
| **Tooling** | [`py-uv`](skills/py-uv/SKILL.md), [`slack`](skills/slack/SKILL.md), [`slack-review-request`](skills/slack-review-request/SKILL.md) | Python packaging, Slack notifications |
| **Meta** | [`skill-create`](skills/skill-create/SKILL.md), [`skill-audit`](skills/skill-audit/SKILL.md), [`skill-index`](skills/skill-index/SKILL.md), [`audit-report`](skills/audit-report/SKILL.md), [`playbook`](skills/playbook/SKILL.md) | Create, audit, and discover skills |

All skills use the `Dev10x:` prefix — type `/Dev10x:git-commit` in the Claude
Code CLI to run it. Run `/Dev10x:skill-index` for the full reference.

## Installation

```
/plugin marketplace add Brave-Labs/Dev10x
/plugin install Dev10x@Brave-Labs
```

[Full installation guide →](docs/installation.md) — prerequisites,
dependencies, manual clone, develop branch, and verification.

## Codex Skills

A Codex-native pack is available in `codex-skills/` for use outside
Claude Code.

[Codex skills guide →](docs/codex.md)

## Community

The [Dev10x community on Skool](https://www.skool.com/Dev10x-1892)
is where plugin users get assistance, request features, and share
workflows. If you already have access to this repository, you do not
need to join Skool — it is a support and discussion hub, not a
gatekeeper for repo access.

## Development

[Development guide →](docs/development.md)
