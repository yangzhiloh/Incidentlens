import typer

from incidentlens import __version__

app = typer.Typer(
    no_args_is_help=True,
    help="Evidence-grounded incident investigation.",
)

@app.callback()
def main() -> None:
    """Evidence-grounded incident investigation."""

@app.command()
def version() -> None:
    """Print the IncidentLens package version."""
    typer.echo(__version__)