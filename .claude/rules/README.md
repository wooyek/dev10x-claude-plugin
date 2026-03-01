# Claude Rules & Agents Directory

Machine-readable rules and agent specifications that Claude follows
during code reviews and interactive assistance. These are **not**
user-facing documentation — they are operational instructions consumed
by Claude Code workflows.

## Architecture

The code review system uses a **multi-agent architecture**:

1. **Orchestrator** (`claude-code-review.yml`) — classifies changed
   files and dispatches to domain-specific agents
2. **Agent specs** (`.claude/agents/`) — focused checklists for each
   review domain
3. **Rules** (`.claude/rules/`) — detailed guidelines referenced by
   agents on demand
4. **Cross-cutting checks** (`review-checks-common.md`) — universal
   checks applied to all domains

## Rules Files

| File                      | Purpose                                   |
|---------------------------|-------------------------------------------|
| `git-commits.md`          | Commit format, branches, gitmoji          |
| `git-pr.md`               | PR format, grooming, review feedback      |
| `git-jtbd.md`             | Job Story format, principles, examples    |
| `github-workflows.md`     | GitHub Actions workflow maintenance rules |
| `review-checks-common.md` | Cross-cutting: false positives, verification |
| `review-guidelines.md`    | How to review: workflow, summaries, threads |
| `skill-naming.md`         | Skill directory and invocation naming     |

## Agent Specs (`.claude/agents/`)

| File                            | Trigger                             | Rules Referenced             |
|---------------------------------|-------------------------------------|------------------------------|
| `reviewer-generic.md`           | `**/*.py`, `**/*.sh`                | `review-checks-common.md`    |
| `reviewer-infra.md`             | `Makefile`, `*.sh`, `bin/**`        | `github-workflows.md`        |
| `reviewer-docs.md`              | `docs/**`, `.claude/**/*.md`        | (self-contained)             |
| `reviewer-rules-maintenance.md` | `.claude/rules/**`, `.claude/agents/**` | (self-contained)         |
| `reviewer-skill.md`             | `skills/**`                         | `skill-naming.md`            |

## Size Budgets

| File type                | Max lines |
|--------------------------|-----------|
| Rule files               | 200       |
| Agent specs              | 50        |
| `review-checks-common.md`| 100      |
| `CLAUDE.md`              | 100       |

When a file reaches 80% of its budget, plan a split.
