import typer

from opportunitylens import __version__

app = typer.Typer(
    no_args_is_help=True,
    help="Evidence-grounded Singapore internship intelligence.",
)


@app.callback()
def main() -> None:
    """Evidence-grounded Singapore internship intelligence."""


@app.command()
def version() -> None:
    """Print the OpportunityLens SG package version."""
    typer.echo(f"OpportunityLens SG {__version__}")
