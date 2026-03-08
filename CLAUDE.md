# dev10x-claude-plugin

Claude Code plugin providing reusable skills, hooks, and commands for
development workflows.

## Directory Layout

This repo is a **single unified `dev10x` plugin** (consolidated from 11
separate plugin directories). All skills, hooks, and config are defined at
the root level.

| Directory        | Purpose                                    |
|------------------|--------------------------------------------|
| `skills/`        | Skill definitions (SKILL.md + scripts)     |
| `commands/`      | Slash command definitions                  |
| `hooks/`         | PreToolUse / PostToolUse hooks             |
| `bin/`           | Helper scripts (release, CI)               |
| `.claude-plugin/`| Plugin manifest (`plugin.json`)            |
| `agents/`        | Plugin-distributed Claude Code sub-agent specs (see `.claude/rules/agents.md`) |
| `references/`    | Shared docs (git, review, JTBD guides)     |
| `.claude/rules/` | Always-loaded essentials + path-scoped rules |
| `.claude/agents/`| Internal domain-specific reviewer agent specs |

## Development

```bash
claude --plugin-dir .          # load plugin locally
claude plugin validate         # validate plugin structure
```

### Testing MCP Servers

```bash
for server in servers/*_server.py; do
  timeout 5 uv run --script "$server" & sleep 2; kill $! 2>/dev/null || true
done
```

MCP migration: shell scripts → MCP tools. See `.claude/rules/mcp-tools.md`.

## Coding Style

- **Python scripts**: ruff + black (line-length 99)
- **Shell scripts**: shellcheck, `set -e`, POSIX-compatible where possible
- **Markdown**: one sentence per line, 80-char soft wrap

## Skill Naming Convention

- **Directory name**: plain feature name — `git-worktree/`, `skill-audit/`
- **Invocation name** (`name:` in SKILL.md): `dev10x:<feature>` — `dev10x:git-worktree`
- The `dev10x:` prefix identifies this plugin's skills at invocation time
  without cluttering the filesystem
- See `.claude/rules/skill-naming.md` for full convention
- **Decision Gates**: Skills with blocking user choice points MUST use
  `AskUserQuestion` tool calls (not plain text). See `.claude/rules/skill-gates.md`

## Git Conventions

- **Default branch**: `develop` (PR target)
- **Release branch**: `main` (merge from develop via release script)
- **Branch naming**: `username/TICKET-ID/short-description`
- **Commit format**: `<gitmoji> <TICKET-ID> <JTBD outcome>`
- **Commit titles**: outcome-focused — "Enable X" not "Add X"
- **Job Story voice** (REQUIRED): First-person "**I want to**" or explicit
  third-party "**so [name] can**" — never objective voice ("wants to")
  See `.claude/rules/essentials.md` and `references/git-jtbd.md` lines 31–45
- See `references/git-commits.md`, `git-pr.md`, `git-jtbd.md`

### Plugin Directory Renames

When renaming a plugin directory (e.g., `plugins/old/ → plugins/new/`):

1. Use `git mv` to preserve history
2. Update `.claude-plugin/marketplace.json` reference
3. Update all SKILL.md files that reference the old path
4. Search codebase for hardcoded directory paths

## Cross-Platform Skill Porting

When porting skills to external platforms (e.g., Codex format):

- **Decision**: Port only stable, well-tested skills with clear reuse cases
- **SKILL.md changes**: Remove Claude-specific fields (contexts, memory hooks);
  keep name, description, usage examples, and invocation specs
- **Validation**: Test ported skills with both `bin/validate-codex-skills.sh`
  and native validation to ensure compatibility
- **Documentation**: Include example showing skill's original and ported forms
- **Commit**: One commit per stable skill or batch of related skills

## Skill Authoring: Formatting as Semantic Signal

Markdown formatting affects agent interpretation of orchestration
directives:

- **Numbered lists** — `TaskCreate` calls in numbered lists are read
  as mandatory instructions to execute at skill startup
- **Code blocks** — the same calls in fenced code blocks (```) are
  read as illustrative examples, not executable
- **Enforcement language** — use `REQUIRED:`, `MANDATORY:`, or `DO NOT SKIP`
  for constraints that must be preserved; pair with imperative language
  (`MUST`, `never`) rather than advisory (`should`, `try to`)

See `.claude/rules/skill-orchestration-format.md` for detailed patterns,
marker guidance, and examples. Review checklist item 14a enforces this.

## Code Review

Multi-agent architecture with domain-routed reviewers:

| Agent spec                      | Trigger                          |
|---------------------------------|----------------------------------|
| `reviewer-generic.md`           | `**/*.py`, `**/*.sh`             |
| `reviewer-infra.md`             | `Makefile`, `bin/**`, `hooks/**`, `*.sh` |
| `reviewer-docs.md`              | `docs/**`, `.claude/**`, `README.md` |
| `reviewer-rules-maintenance.md` | `.claude/rules/**`, `.claude/agents/**` |
| `reviewer-skill.md`             | `skills/**`                      |

See `.claude/rules/README.md` for the full architecture.
