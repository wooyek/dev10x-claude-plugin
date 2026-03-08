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
| `.claude/rules/agents.md` | When editing `agents/**` | Plugin-distributed agent specs |
| `.claude/rules/github-workflows.md` | When editing `.github/workflows/**` | GitHub Actions patterns |
| `.claude/rules/mcp-tools.md` | When editing `servers/**` or MCP-related skills | MCP tool naming, versioning, availability |
| `references/*.md` | On-demand by skills/CI | Detailed git, review, JTBD guides |

## Reference Documents (`references/`)

| File | Topic | Loaded by | Scope |
|------|-------|-----------|-------|
| `git-commits.md` | Commit format, gitmoji, atomic commits | `dev10x:git-commit` skill, PR hygiene CI | Mandatory for all commits |
| `git-pr.md` | PR format, grooming, review feedback | `dev10x:gh-pr-create` skill, PR hygiene CI | Mandatory for all PRs |
| `git-jtbd.md` | Job Story format, principles, examples | `dev10x:jtbd` skill, PR hygiene CI | Mandatory for JTBD decisions |
| `review-guidelines.md` | Review workflow, threads, summaries | `dev10x:gh-pr-review` skill, code review CI | Mandatory for PR reviews |
| `review-checks-common.md` | False positives, verification | Review agent specs, code review CI | Mandatory for code review agents |
| `eval-schema.md` | Evaluation assertions format for skills | `reviewer-skill.md` (item 19) | Decision gate validation |
| `skill-invocation.md` | Skill() syntax, named parameters, delegation | `reviewer-skill.md` (items 8g, 9a) | Mandatory for skill reviews |
| `task-orchestration.md` | Orchestration patterns, auto-advance, batched decisions | All skills (via `## Orchestration` section) | Referenced, not auto-loaded |

## Agent Specs (`.claude/agents/`)

Internal review-only agents (≤ 50 lines each).

| File | Trigger | References |
|------|---------|------------|
| `reviewer-generic.md` | `**/*.py`, `**/*.sh` | `references/review-checks-common.md` |
| `reviewer-infra.md` | `Makefile`, `**/*.sh`, `bin/**`, `.github/workflows/**` | `references/review-checks-common.md` |
| `reviewer-docs.md` | `docs/**`, `.claude/**/*.md` | `references/review-checks-common.md` |
| `reviewer-rules-maintenance.md` | `.claude/rules/**`, `.claude/agents/**`, `agents/**` | (self-contained) |
| `reviewer-rules-structure.md` | `.claude/rules/**/*.md`, `.claude/agents/**/*.md` | (self-contained) |
| `reviewer-skill.md` | `skills/**`, `codex-skills/**` | `.claude/rules/skill-naming.md` |

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

## Budget Overrides

File size budgets (200 lines for reference docs, 50 for agent specs, 100 for CLAUDE.md) are guidelines to prevent sprawl. Exceptions are permitted when:

1. **Content is semantically cohesive** — splitting would obscure relationships between concepts
2. **All consumers link to a single file** — multi-file splits would increase maintenance burden
3. **Author justification is explicit** — the rationale for keeping the file together is documented in the PR
4. **A split plan is conditional** — if maintenance becomes problematic, the team commits to splitting by [topic/pattern group]

Examples:
- `references/task-orchestration.md` (367 lines) exceeds the 200-line budget because 7 orchestration patterns form a unified framework that 43+ skills reference atomically. Splitting would force each skill to track multiple files.
- `.claude/agents/reviewer-skill.md` (151 lines) exceeds the 50-line budget because skill review spans 19 distinct checklist items covering naming, scripting, tooling, behavioral constraints, and config management. If the file exceeds 170 lines, split into `reviewer-skill-paths.md` (items 7–8g) and `reviewer-skill-behavior.md` (items 14–19).

Reviewers must flag overrides with `[OVERRIDE DETECTED]` comments and verify:
- Cohesion justification is clear
- A conditional split plan exists (e.g., "if file exceeds 400 lines, extract patterns 5-7")
- The author acknowledges the override explicitly
