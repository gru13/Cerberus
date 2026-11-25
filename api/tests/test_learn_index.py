"""Intent: Test the learning index check on small sample files."""

import urllib.error
from pathlib import Path

import learn_index
import pytest

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


def test_online_runs_offline_rules_first(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    requested: list[str] = []
    monkeypatch.setattr(learn_index, "url_is_alive", lambda u: requested.append(u) or True)
    text = VALID.replace("https://man7.org", "https://example.com")
    assert learn_index.check_online(write(tmp_path, text)) == 1
    assert requested == []


def test_online_checks_llms_txt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    requested: list[str] = []
    monkeypatch.setattr(learn_index, "url_is_alive", lambda u: requested.append(u) or True)
    text = VALID + "    llms_txt: https://man7.org/llms.txt\n"
    assert learn_index.check_online(write(tmp_path, text)) == 0
    assert "https://man7.org/llms.txt" in requested


def test_online_reports_dead_link(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(learn_index, "url_is_alive", lambda _u: False)
    assert learn_index.check_online(write(tmp_path, VALID)) == 1


class FakeResponse:
    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None


def test_get_after_failed_head(monkeypatch: pytest.MonkeyPatch) -> None:
    methods: list[str] = []

    def fake_urlopen(request: learn_index.urllib.request.Request, timeout: int) -> FakeResponse:
        methods.append(request.get_method())
        if request.get_method() == "HEAD":
            reason = "head refused"
            raise urllib.error.URLError(reason)
        return FakeResponse()

    monkeypatch.setattr(learn_index.urllib.request, "urlopen", fake_urlopen)
    assert learn_index.url_is_alive("https://man7.org/x")
    assert methods == ["HEAD", "GET"]


def test_both_methods_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: learn_index.urllib.request.Request, timeout: int) -> FakeResponse:
        raise TimeoutError

    monkeypatch.setattr(learn_index.urllib.request, "urlopen", fake_urlopen)
    assert not learn_index.url_is_alive("https://man7.org/x")


def test_malformed_url_is_dead() -> None:
    assert not learn_index.url_is_alive("not a url")


def test_cli_usage_error(tmp_path: Path) -> None:
    path = write(tmp_path, VALID)
    assert learn_index.main(["learn_index.py"], path) == 2
    assert learn_index.main(["learn_index.py", "build"], path) == 2
    assert learn_index.main(["learn_index.py", "check"], path) == 0


def test_real_sources_file_passes() -> None:
    assert learn_index.check_offline(learn_index.SOURCES_FILE) == 0
