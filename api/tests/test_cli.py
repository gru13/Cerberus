import pytest
from typer.testing import CliRunner

from cerberus import __version__
from cerberus.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == f"cerberus {__version__}"


def test_doctor_passes() -> None:
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "All checks pass." in result.output


@pytest.mark.parametrize(("command", "story"), [("worker", "8.5.1"), ("migrate", "8.2.3")])
def test_placeholder_commands_fail_clearly(command: str, story: str) -> None:
    result = runner.invoke(app, [command])

    assert result.exit_code == 1
    assert f"Story {story} adds it." in result.output


def test_no_args_shows_help() -> None:
    result = runner.invoke(app, [])

    assert "api" in result.output
    assert "doctor" in result.output
