# Claude Rules & Agents Directory

Machine-readable rules and agent specifications that Claude follows
during code reviews and interactive assistance.

## Architecture

The code review system uses a **multi-agent architecture**:

1. **Orchestrator** (`claude-code-review.yml`) — classifies changed
   files and dispatches to domain-specific agents
2. **Agent specs** (`.claude/agents/`) — focused checklists for each
   review domain
3. **Rules** (`.claude/rules/`) — always-loaded essentials and
   path-scoped rules
4. **References** (`references/`) — detailed guides loaded on-demand
   by skills and CI workflows

## Loading Strategy

| Location | When loaded | Content |
|----------|------------|---------|
| `.claude/rules/essentials.md` | Every session | Universal conventions (~36 lines) |
| `.claude/rules/skill-naming.md` | When editing `skills/**` | Skill naming conventions |
| `.claude/rules/github-workflows.md` | When editing `.github/workflows/**` | GitHub Actions patterns |
| `references/*.md` | On-demand by skills/CI | Detailed git, review, JTBD guides |

## Reference Documents (`references/`)

| File | Topic | Loaded by |
|------|-------|-----------|
| `git-commits.md` | Commit format, gitmoji, atomic commits | `dx:git-commit` skill, PR hygiene CI |
| `git-pr.md` | PR format, grooming, review feedback | `dx:gh-pr-create` skill, PR hygiene CI |
| `git-jtbd.md` | Job Story format, principles, examples | `dx:jtbd` skill, PR hygiene CI |
| `review-guidelines.md` | Review workflow, threads, summaries | `dx:gh-pr-review` skill, code review CI |
| `review-checks-common.md` | False positives, verification | Review agent specs, code review CI |

## Agent Specs (`.claude/agents/`)

Internal review-only agents (≤ 50 lines each).

| File | Trigger | References |
|------|---------|------------|
| `reviewer-generic.md` | `**/*.py`, `**/*.sh` | `references/review-checks-common.md` |
| `reviewer-infra.md` | `Makefile`, `**/*.sh`, `bin/**`, `.github/workflows/**` | `references/review-checks-common.md` |
| `reviewer-docs.md` | `docs/**`, `.claude/**/*.md` | `references/review-checks-common.md` |
| `reviewer-rules-maintenance.md` | `.claude/rules/**`, `.claude/agents/**`, `agents/**` | (self-contained) |
| `reviewer-skill.md` | `skills/**` | `.claude/rules/skill-naming.md` |

## Plugin-Distributed Sub-Agents (`agents/`)

Sub-agent specs shipped with the plugin for user workflows (≤ 200 lines each).
Distinct from `.claude/agents/` — these are operational agents, not review
checklists, and need full phase logic and examples.

| File | Purpose |
|------|---------|
| `agents/<name>.md` | Plugin sub-agent spec (e.g., `permission-auditor.md`) |

## Size Budgets

| File type | Max lines |
|-----------|-----------|
| Rule files | 200 |
| Agent specs | 50 |
| Reference docs | 200 |
| `CLAUDE.md` | 100 |

When a file reaches 80% of its budget, plan a split.
