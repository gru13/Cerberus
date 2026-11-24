"""FastAPI application factory."""

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

from cerberus import __version__

API_PREFIX = "/api/v1"


class HelloResponse(BaseModel):
    """Reply of the hello endpoint."""

    message: str
    version: str


def create_app() -> FastAPI:
    """Create the Cerberus API application."""
    app = FastAPI(title="Cerberus API", version=__version__)
    router = APIRouter(prefix=API_PREFIX)

    @router.get("/hello", operation_id="hello")
    def hello() -> HelloResponse:
        """Return a short message that shows the API is running."""
        return HelloResponse(message="The Cerberus API is ready.", version=__version__)

    app.include_router(router)
    return app


app = create_app()
