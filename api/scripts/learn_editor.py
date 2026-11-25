"""Intent: Serve a local browser editor for the learning index YAML files.

Why: A small local server lets the page save; every save passes the same rules as the check.
"""

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

import uvicorn
from fastapi import FastAPI, Header, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from learn_models import LearnIndex, LearnIndexError, stale_warnings, validate_index
from learn_store import LEARN_DIR, index_tag, load_index, save_index
from pydantic import BaseModel, ConfigDict

PAGE_FILE = Path(__file__).with_name("learn_editor.html")
HOST = "127.0.0.1"
PORT = 8765


class IndexView(BaseModel):
    """The index with its version tag and stale warnings, as the page reads it."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tag: str
    warnings: list[str]
    index: LearnIndex


class SaveResult(BaseModel):
    """The result of one save: the new version tag, or the rule problems."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tag: str | None = None
    problems: list[str] = []


class StaleTagError(LearnIndexError):
    """The file changed after the page loaded it."""

    code: ClassVar[str] = "learn.index.stale"
    message: ClassVar[str] = "The index files change after you load them. Load them again."


def problem_response(status: int, problems: list[str]) -> JSONResponse:
    """Return a JSON response that lists rule problems."""
    return JSONResponse(SaveResult(problems=problems).model_dump(), status_code=status)


def create_app(path: Path = LEARN_DIR) -> FastAPI:
    """Create the editor app for one learning index folder.

    Functional: GET / gives the page; GET /api/index gives the data; PUT /api/index saves.
    Technical: PUT needs the `If-Match` tag from the last GET (optimistic lock on the file
        hashes). It validates with Pydantic and `validate_index`, then writes atomically.
    Errors: 409 when the tag is old; 422 when a rule fails.
    """
    app = FastAPI(title="Cerberus learning index editor", docs_url=None, redoc_url=None)

    @app.exception_handler(LearnIndexError)
    async def rule_error(_request: Request, error: LearnIndexError) -> JSONResponse:
        """Map a concept rule error to 422, and a stale tag to 409."""
        status = 409 if isinstance(error, StaleTagError) else 422
        return problem_response(status, [f"{error.message} {error.details}"])

    @app.get("/")
    async def page() -> FileResponse:
        """Return the editor page."""
        return FileResponse(PAGE_FILE)

    @app.get("/api/index")
    async def read_index() -> IndexView:
        """Return the index, its version tag, and its stale warnings."""
        index = load_index(path)
        warnings = stale_warnings(index, datetime.now(UTC).date())
        return IndexView(tag=index_tag(path), warnings=warnings, index=index)

    @app.put("/api/index", response_model=None)
    async def write_index(
        index: LearnIndex, if_match: str = Header(default="")
    ) -> SaveResult | Response:
        """Save the index when the tag is current and every rule passes.

        Functional: Writes nothing when the tag is old or a rule fails.
        Technical: Compares `If-Match` with the file hash, then runs `validate_index`.
        Errors: StaleTagError (old tag, 409); LearnIndexError (concept rule, 422).
        """
        if if_match != index_tag(path):
            raise StaleTagError(details={"rule": "if-match"})
        problems = validate_index(index)
        if problems:
            return problem_response(422, problems)
        save_index(path, index)
        return SaveResult(tag=index_tag(path))

    return app


def main() -> int:
    """Start the editor on http://127.0.0.1:8765 and return when it stops."""
    print(f"The editor runs at http://{HOST}:{PORT}. Press Ctrl+C to stop.")
    uvicorn.run(create_app(), host=HOST, port=PORT, log_level="warning")
    return 0


if __name__ == "__main__":
    sys.exit(main())
