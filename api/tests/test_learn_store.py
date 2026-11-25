"""Intent: Test the learning index storage in its split YAML layout."""

from pathlib import Path

import learn_store
import pytest
from learn_models import LearnIndexError

from test_learn_index import VALID, write


def test_dump_round_trips(tmp_path: Path) -> None:
    index = learn_store.load_index(write(tmp_path, VALID))
    again = tmp_path / "again"
    again.mkdir()
    learn_store.save_index(again, index)
    assert learn_store.load_index(again) == index


def test_unknown_area_file_fails(tmp_path: Path) -> None:
    path = write(tmp_path, VALID)
    (path / "concepts" / "misc.yaml").write_text("[]\n", encoding="utf-8")
    with pytest.raises(LearnIndexError):
        learn_store.load_index(path)


def test_area_key_in_entry_fails(tmp_path: Path) -> None:
    path = write(tmp_path, VALID)
    area_file = path / "concepts" / "sandbox.yaml"
    text = area_file.read_text(encoding="utf-8").replace("- id:", "- area: sandbox\n  id:")
    area_file.write_text(text, encoding="utf-8")
    with pytest.raises(LearnIndexError):
        learn_store.load_index(path)


def test_concepts_in_settings_file_fail(tmp_path: Path) -> None:
    path = write(tmp_path, VALID)
    (path / "index.yaml").write_text("version: 1\nconcepts: []\n", encoding="utf-8")
    with pytest.raises(LearnIndexError):
        learn_store.load_index(path)


def test_moving_last_concept_removes_area_file(tmp_path: Path) -> None:
    path = write(tmp_path, VALID)
    index = learn_store.load_index(path)
    moved = index.concepts[0].model_copy(update={"id": "realtime.openat2", "area": "realtime"})
    learn_store.save_index(path, index.model_copy(update={"concepts": [moved]}))
    assert not (path / "concepts" / "sandbox.yaml").exists()
    assert learn_store.load_index(path).concepts[0].area == "realtime"
