from fastapi.testclient import TestClient

from cerberus import __version__
from cerberus.main import create_app


def test_hello_returns_ready_message() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "The Cerberus API is ready.", "version": __version__}


def test_openapi_lists_hello() -> None:
    client = TestClient(create_app())

    spec = client.get("/openapi.json").json()

    assert spec["paths"]["/api/v1/hello"]["get"]["operationId"] == "hello"
