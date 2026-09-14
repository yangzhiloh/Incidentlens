from typer.testing import CliRunner

from opportunitylens.cli import app

runner = CliRunner()


def test_cli_reports_opportunitylens_name() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "OpportunityLens SG" in result.stdout
