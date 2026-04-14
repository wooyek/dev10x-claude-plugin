# Performance Baselines

Documented performance metrics for regression tracking.

## CLI Startup Time

**Target:** < 200ms for `dev10x --help`

**Baseline (2026-04-14):** ~40ms via `uv run dev10x --help`

**Architecture:** Click LazyGroup pattern (`src/dev10x/cli.py`)
defers all subcommand imports until invocation. Only `click`,
`importlib`, and `typing` are loaded at startup.

**Hot imports (from `-X importtime`):**

| Import | Self (us) | Cumulative (us) |
|--------|-----------|-----------------|
| `click.core` | 942 | 10,356 |
| `inspect` | 1,152 | 5,522 |
| `typing` | 1,162 | 2,608 |
| `ast` | 794 | 2,640 |
| `site` | 673 | 2,092 |

These are click framework and Python stdlib — not optimizable
without replacing the framework. Current lazy loading covers
all dev10x subcommands.

## Monitoring

Run `time uv run dev10x --help` after dependency changes.
If startup exceeds 200ms, profile with:
```bash
uv run python -X importtime -c "from dev10x.cli import cli" \
  2>&1 | sort -t: -k2 -n | tail -20
```
