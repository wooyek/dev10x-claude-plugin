import click


@click.group()
@click.version_option(package_name="Dev10x")
def cli() -> None:
    pass
