"""Intent: Provide the `cerberus` command line interface (api, worker, migrate, doctor)."""

import sys
from typing import Annotated

import typer

from cerberus import __version__

app = typer.Typer(
    name="cerberus",
    help="Cerberus platform commands.",
    no_args_is_help=True,
    add_completion=False,
)

MIN_PYTHON = (3, 14)


def _version_callback(value: bool) -> None:
    """Print the version and stop when `--version` is given."""
    if value:
        typer.echo(f"cerberus {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version", callback=_version_callback, is_eager=True, help="Show the version."
        ),
    ] = False,
) -> None:
    """Cerberus platform commands."""


@app.command()
def api(
    host: Annotated[
        str, typer.Option(help="Address to bind. Keep 127.0.0.1 in local mode.")
    ] = "127.0.0.1",
    port: Annotated[int, typer.Option(help="Port to listen on.")] = 8000,
    reload: Annotated[
        bool, typer.Option(help="Reload on code changes (development only).")
    ] = False,
) -> None:
    """Start the HTTP API server."""
    import uvicorn

    uvicorn.run("cerberus.main:app", host=host, port=port, reload=reload)


def _not_ready(command: str, story: str) -> None:
    """Tell the user that a command does not exist yet, then exit with code 1."""
    typer.echo(f"The {command} command is not ready. Story {story} adds it.", err=True)
    raise typer.Exit(code=1)


@app.command()
def worker() -> None:
    """Start the job worker (story 8.5.1)."""
    _not_ready("worker", "8.5.1")


@app.command()
def migrate() -> None:
    """Apply database migrations (story 8.2.3)."""
    _not_ready("migrate", "8.2.3")


@app.command()
def doctor() -> None:
    """Check that this machine can run Cerberus.

    Functional: Prints PASS or FAIL per check and exits 1 when any check fails.
    Technical: Checks the Python version and that the FastAPI app loads; later stories add checks.
    """
    ok = True
    if sys.version_info[:2] >= MIN_PYTHON:
        typer.echo(f"PASS The Python version is {sys.version.split()[0]}.")
    else:
        ok = False
        typer.echo(
            f"FAIL The Python version must be 3.14 or later. It is {sys.version.split()[0]}."
        )
    try:
        from cerberus.main import create_app

        create_app()
        typer.echo("PASS The API application loads.")
    # Why: doctor is a boundary; it must report any load failure instead of crashing.
    except Exception as exc:  # noqa: BLE001
        ok = False
        typer.echo(f"FAIL The API application does not load: {type(exc).__name__}.")
    if not ok:
        raise typer.Exit(code=1)
    typer.echo("All checks pass.")
