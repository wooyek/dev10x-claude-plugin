# dev10x-claude-plugin

Claude Code plugin providing reusable skills, hooks, and commands for
development workflows.

## Directory Layout

| Directory        | Purpose                                    |
|------------------|--------------------------------------------|
| `skills/`        | Skill definitions (SKILL.md + scripts)     |
| `commands/`      | Slash command definitions                  |
| `hooks/`         | PreToolUse / PostToolUse hooks             |
| `bin/`           | Helper scripts (release, CI)               |
| `.claude-plugin/`| Plugin manifest (`plugin.json`)            |
| `.claude/rules/` | Machine-readable rules for reviews         |
| `.claude/agents/`| Domain-specific reviewer agent specs       |

## Development

```bash
claude --plugin-dir .          # load plugin locally
claude plugin validate         # validate plugin structure
```

## Coding Style

- **Python scripts**: ruff + black (line-length 99)
- **Shell scripts**: shellcheck, `set -e`, POSIX-compatible where possible
- **Markdown**: one sentence per line, 80-char soft wrap

## Skill Naming Convention

- **Directory name**: plain feature name — `git-worktree/`, `skill-audit/`
- **Invocation name** (`name:` in SKILL.md): `dx:<feature>` — `dx:git-worktree`
- The `dx:` prefix identifies this plugin's skills at invocation time
  without cluttering the filesystem
- See `.claude/rules/skill-naming.md` for full convention

## Git Conventions

- **Default branch**: `develop` (PR target)
- **Release branch**: `main` (merge from develop via release script)
- **Branch naming**: `username/TICKET-ID/short-description`
- **Commit format**: `<gitmoji> <TICKET-ID> <JTBD outcome>`
- **Commit titles**: outcome-focused — "Enable X" not "Add X"
- See `.claude/rules/git-commits.md`, `git-pr.md`, `git-jtbd.md`

## Code Review

Multi-agent architecture with domain-routed reviewers:

| Agent spec                      | Trigger                          |
|---------------------------------|----------------------------------|
| `reviewer-generic.md`           | `**/*.py`, `**/*.sh`             |
| `reviewer-infra.md`             | `Makefile`, `bin/**`, `*.sh`     |
| `reviewer-docs.md`              | `docs/**`, `.claude/**`, `README.md` |
| `reviewer-rules-maintenance.md` | `.claude/rules/**`, `.claude/agents/**` |
| `reviewer-skill.md`             | `skills/**`                      |

See `.claude/rules/README.md` for the full architecture.
