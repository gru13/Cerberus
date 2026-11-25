"""Intent: Test the learning index editor API, including its YAML writer."""

from pathlib import Path

import learn_store
from fastapi.testclient import TestClient
from learn_editor import create_app

from test_learn_index import VALID, write


def client_for(tmp_path: Path) -> tuple[TestClient, Path]:
    path = write(tmp_path, VALID)
    return TestClient(create_app(path)), path


def test_page_is_served(tmp_path: Path) -> None:
    client, _ = client_for(tmp_path)
    response = client.get("/")
    assert response.status_code == 200
    assert "Learning index" in response.text


def test_read_returns_index_and_tag(tmp_path: Path) -> None:
    client, path = client_for(tmp_path)
    body = client.get("/api/index").json()
    assert body["tag"] == learn_store.file_tag(path)
    assert body["index"]["concepts"][0]["id"] == "sandbox.openat2"


def test_save_writes_canonical_yaml(tmp_path: Path) -> None:
    client, path = client_for(tmp_path)
    body = client.get("/api/index").json()
    body["index"]["concepts"][0]["title"] = "openat2 (changed)"
    response = client.put("/api/index", json=body["index"], headers={"If-Match": body["tag"]})
    assert response.status_code == 200
    assert response.json()["tag"] == learn_store.file_tag(path)
    text = path.read_text(encoding="utf-8")
    assert "title: openat2 (changed)" in text
    assert "notes: |" in text


def test_save_with_old_tag_is_refused(tmp_path: Path) -> None:
    client, path = client_for(tmp_path)
    body = client.get("/api/index").json()
    before = path.read_text(encoding="utf-8")
    response = client.put("/api/index", json=body["index"], headers={"If-Match": "old"})
    assert response.status_code == 409
    assert path.read_text(encoding="utf-8") == before


def test_save_with_bad_domain_is_refused(tmp_path: Path) -> None:
    client, path = client_for(tmp_path)
    body = client.get("/api/index").json()
    body["index"]["concepts"][0]["sources"][0]["url"] = "https://example.com/x"
    response = client.put("/api/index", json=body["index"], headers={"If-Match": body["tag"]})
    assert response.status_code == 422
    assert "not allowed" in response.json()["problems"][0]
    assert "example.com" not in path.read_text(encoding="utf-8")


def test_save_without_primary_source_is_refused(tmp_path: Path) -> None:
    client, _ = client_for(tmp_path)
    body = client.get("/api/index").json()
    body["index"]["concepts"][0]["sources"][0]["primary"] = False
    response = client.put("/api/index", json=body["index"], headers={"If-Match": body["tag"]})
    assert response.status_code == 422


def test_dump_round_trips(tmp_path: Path) -> None:
    index = learn_store.load_index(write(tmp_path, VALID))
    again = tmp_path / "again.yaml"
    learn_store.save_index(again, index)
    assert learn_store.load_index(again) == index
