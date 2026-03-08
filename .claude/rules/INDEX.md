# Rule Index & Agent Routing

Path-aware routing table. Match changed files to agents, then load
only listed reference files.

## Directory Contract

- This file is the single source of truth in `.claude/rules/`.
- Full rule content lives in `references/*.md`.
- Agent triggers and checklists live in `.claude/agents/*.md`.
- Path-scoped rules (e.g., `skill-naming.md`) load conditionally.

## File Patterns -> Agents -> References

| File Pattern | Primary Agent | Required References |
|---|---|---|
| `**/*.py`, `**/*.sh` | `reviewer-generic` | `references/review-checks-common.md` |
| `Makefile`, `bin/**`, `hooks/**`, `*.sh` | `reviewer-infra` | `references/review-checks-common.md` |
| `docs/**`, `.claude/**/*.md`, `README.md` | `reviewer-docs` | `references/review-checks-common.md` |
| `.claude/rules/**`, `.claude/agents/**`, `agents/**` | `reviewer-rules-maintenance` | (self-contained) |
| `skills/**` | `reviewer-skill` | `.claude/rules/skill-naming.md`, `references/skill-invocation.md`, `references/eval-schema.md` |

## Loading Order

1. Always load `CLAUDE.md`, `essentials.md`, and this `INDEX.md`.
2. Match changed files to agent(s) above.
3. Load only required references for matched agents.
4. Path-scoped rules (`skill-naming.md`, `agents.md`,
   `github-workflows.md`) load per their scope annotations.

## Cross-Cutting Checks

Always apply `references/review-checks-common.md`.
