import click


@click.group()
def hook() -> None:
    """Hook entry points (validate-bash, validate-edit, plan-sync, session)."""
