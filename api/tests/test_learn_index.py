"""Intent: Test the learning index tool on small sample files."""

from pathlib import Path

import learn_index

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
    path = tmp_path / "sources.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_valid_file_passes(tmp_path: Path) -> None:
    assert learn_index.check_offline(write(tmp_path, VALID)) == 0


def test_bad_domain_fails(tmp_path: Path) -> None:
    text = VALID.replace("https://man7.org", "https://example.com")
    assert learn_index.check_offline(write(tmp_path, text)) == 1


def test_duplicate_id_fails(tmp_path: Path) -> None:
    concept = VALID.split("concepts:\n")[1]
    assert learn_index.check_offline(write(tmp_path, VALID + concept)) == 1


def test_missing_primary_source_fails(tmp_path: Path) -> None:
    path = write(tmp_path, VALID.replace("primary: true", "primary: false"))
    assert learn_index.check_offline(path) == 1


def test_build_writes_pages(tmp_path: Path) -> None:
    source = write(tmp_path, VALID)
    assert learn_index.build(source, tmp_path) == 0
    assert '<a id="sandbox.openat2"></a>' in (tmp_path / "sandbox.md").read_text()
