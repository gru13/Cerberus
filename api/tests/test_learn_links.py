"""Intent: Test the online link check of the learning index."""

import urllib.error
from pathlib import Path

import learn_index
import pytest

from test_learn_index import VALID, write


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
