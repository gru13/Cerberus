"""Intent: Test the learning index check on small sample files."""

from pathlib import Path

import learn_index
import yaml

VALID = """
version: 1
stale_after_days: 90
allowed_domains: [man7.org]
concepts:
  - id: sandbox.openat2
    title: openat2
    area: sandbox
    stories: ["4.3.2"]
    phase: P1
    notes: |
      Opens a path under a directory.
    sources:
      - url: https://man7.org/linux/man-pages/man2/openat2.2.html
        title: openat2(2)
        kind: man-page
        publisher: Linux man-pages project
        version: "Linux 5.6+"
        primary: true
        checked: 2026-11-25
"""


def write(tmp_path: Path, text: str) -> Path:
    """Write sample YAML (settings plus concepts) in the split layout; return the folder."""
    data = yaml.safe_load(text)
    concepts = data.pop("concepts")
    (tmp_path / "index.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    (tmp_path / "concepts").mkdir(exist_ok=True)
    by_area: dict[str, list[dict[str, object]]] = {}
    for concept in concepts:
        by_area.setdefault(concept.pop("area"), []).append(concept)
    for area, entries in by_area.items():
        path = tmp_path / "concepts" / f"{area}.yaml"
        path.write_text(yaml.safe_dump(entries, sort_keys=False), encoding="utf-8")
    return tmp_path


def test_valid_file_passes(tmp_path: Path) -> None:
    assert learn_index.check_offline(write(tmp_path, VALID)) == 0


def test_bad_domain_fails(tmp_path: Path) -> None:
    text = VALID.replace("https://man7.org", "https://example.com")
    assert learn_index.check_offline(write(tmp_path, text)) == 1


def test_http_link_fails(tmp_path: Path) -> None:
    text = VALID.replace("https://man7.org", "http://man7.org")
    assert learn_index.check_offline(write(tmp_path, text)) == 1


def test_llms_txt_on_bad_domain_fails(tmp_path: Path) -> None:
    text = VALID + "    llms_txt: https://example.com/llms.txt\n"
    assert learn_index.check_offline(write(tmp_path, text)) == 1


def test_duplicate_id_fails(tmp_path: Path) -> None:
    concept = VALID.split("concepts:\n")[1]
    assert learn_index.check_offline(write(tmp_path, VALID + concept)) == 1


def test_missing_primary_source_fails(tmp_path: Path) -> None:
    path = write(tmp_path, VALID.replace("primary: true", "primary: false"))
    assert learn_index.check_offline(path) == 1


def test_cli_usage_error(tmp_path: Path) -> None:
    path = write(tmp_path, VALID)
    assert learn_index.main(["learn_index.py"], path) == 2
    assert learn_index.main(["learn_index.py", "build"], path) == 2
    assert learn_index.main(["learn_index.py", "check"], path) == 0


def test_real_sources_file_passes() -> None:
    assert learn_index.check_offline(learn_index.LEARN_DIR) == 0
