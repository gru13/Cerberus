"""Intent: Build the FastAPI application that serves the Cerberus HTTP API."""

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, ConfigDict

from cerberus import __version__

API_PREFIX = "/api/v1"


class HelloResponse(BaseModel):
    """Reply of the hello endpoint."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    message: str
    version: str


def create_app() -> FastAPI:
    """Create the Cerberus API application.

    Functional: Returns an app that answers `GET /api/v1/hello` with a ready message.
    Technical: FastAPI app factory; routes live on one `APIRouter` under `/api/v1`.
    """
    app = FastAPI(title="Cerberus API", version=__version__)
    router = APIRouter(prefix=API_PREFIX)

    @router.get("/hello", operation_id="hello")
    def hello() -> HelloResponse:
        """Return a short message that shows the API is running."""
        return HelloResponse(message="The Cerberus API is ready.", version=__version__)

    app.include_router(router)
    return app


app = create_app()
