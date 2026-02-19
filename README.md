# dev10x-db

A Claude Code plugin for safe database query planning and execution.

## What it does

- **Schema-first query construction** - Claude checks project schemas before writing SQL
- **Read-only safety** - SQL validation hook blocks write operations
- **Convention-based context discovery** - auto-discovers `memory/db-*-schema.md` files and `*:db` skills
- **psql wrapper** - `db.sh` script with alias-based database selection from `databases.json`

## Install

```
/plugin add github:wooyek/dev10x-claude-plugin
```

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| `dev10x-db` | Agent (auto) | Query planning workflow and schema discovery conventions |
| `dev10x-db-psql` | User-invocable | psql execution wrapper with SQL validation |

## Setup

1. Install the plugin
2. Create a `databases.json` in your project's skill directory (see `databases.json.example`)
3. Set database DSN environment variables in your shell profile
4. Add permission rules for `db.sh` to your Claude Code settings

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
