from __future__ import annotations

import sys
from pathlib import Path

import click


@click.group()
def skill() -> None:
    """Skill script commands (audit, notify, permission, release-notes)."""


@skill.command(name="count-instructions")
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(exists=True, path_type=Path),
    required=True,
)
@click.option(
    "--warn",
    type=int,
    default=None,
    help="Threshold at which to flag the file (default: 100).",
)
@click.option(
    "--over",
    type=int,
    default=None,
    help="Threshold above which to exit non-zero (default: 150).",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Print only over-threshold files.",
)
def count_instructions(
    *,
    paths: tuple[Path, ...],
    warn: int | None,
    over: int | None,
    quiet: bool,
) -> None:
    """Count actionable instructions per skill file (GH-882 instruction budget).

    QRSPI finding: LLMs follow ~150–200 instructions reliably, then silently
    skip the rest. Large skills that cross this budget risk dropping alignment
    steps without any error signal.

    Accepts individual SKILL.md files or directories (scanned recursively).
    Exit code 1 if any file exceeds --over (default 150).
    """
    from dev10x.skills.audit import instruction_budget as mod

    w = warn if warn is not None else mod.DEFAULT_WARN
    o = over if over is not None else mod.DEFAULT_OVER

    files: list[Path] = []
    for p in paths:
        if p.is_dir():
            files.extend(mod.find_skill_files(p))
        elif p.is_file():
            files.append(p)

    if not files:
        click.echo("No SKILL.md files found.")
        sys.exit(0)

    reports = mod.scan(files, warn=w, over=o)

    max_width = max((len(str(r.path)) for r in reports), default=40)
    over_count = 0
    warn_count = 0

    for report in reports:
        marker = {"ok": " ", "warn": "!", "over": "✗"}[report.status]
        if report.status == "over":
            over_count += 1
        elif report.status == "warn":
            warn_count += 1
        if quiet and report.status == "ok":
            continue
        click.echo(f" {marker} {str(report.path):<{max_width}}  {report.count:>4}")

    click.echo()
    click.echo(f"Thresholds: warn ≥ {w}, over ≥ {o}")
    click.echo(f"Scanned {len(reports)} file(s): {warn_count} warn, {over_count} over.")

    sys.exit(1 if over_count > 0 else 0)
