from importlib.metadata import PackageNotFoundError, distribution

import pytest


def test_installed_distribution_exposes_only_opportunitylens_command() -> None:
    try:
        package = distribution("opportunitylens")
    except PackageNotFoundError:
        pytest.fail("the OpportunityLens distribution is not installed")

    console_scripts = {
        entry_point.name: entry_point.value
        for entry_point in package.entry_points
        if entry_point.group == "console_scripts"
    }

    assert console_scripts == {"opportunitylens": "opportunitylens.cli:app"}
