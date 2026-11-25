# /// script
# requires-python = ">=3.13"
# dependencies = ["pydantic>=2.12", "pyyaml>=6.0.2"]
# ///
"""Intent: One tool for the learning index YAML: check it, check its links, edit it in a browser.

Why: A single standalone file keeps the learning index self-contained in docs/learn; it does not
    depend on the API package. Its errors use a local LearnIndexError, not CerberusError, for
    that reason. It is above 300 lines because the editor page is embedded in it.
Usage: uv run docs/learn/learn.py check | check --online | edit
"""

import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import UTC, date, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Literal, get_args
from urllib.parse import urlparse

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

LEARN_DIR = Path(__file__).resolve().parent
SETTINGS_NAME = "index.yaml"
CONCEPTS_DIR = "concepts"
HOST, PORT = "127.0.0.1", 8765
MAX_BODY_BYTES = 5_000_000
TIMEOUT_SECONDS = 10
USAGE = "Usage: uv run docs/learn/learn.py check | check --online | edit"

type SourceKind = Literal["official-docs", "api-reference", "man-page", "spec", "project-repo"]
type Area = Literal["sandbox", "realtime", "persistence", "security", "protocol", "build"]
type YamlData = Any
AREAS: tuple[str, ...] = get_args(Area.__value__)

SETTINGS_HEADER = """\
# Learning index: settings. Edit by hand or with `uv run docs/learn/learn.py edit`.
# The concepts live in concepts/<area>.yaml, one file per area; this file has no concepts.
# version: format version. stale_after_days: a source checked longer ago gives a warning.
# allowed_domains: the only hosts a source or llms_txt link may use (https only).
# Policy: official sources only; notes in our own words. Check: learn.py check.
"""
AREA_HEADER = """\
# Learning index: {area} concepts. The area comes from this file name; entries have no area key.
# Each entry: id (<area>.<name>), title, stories (guided story ids), phase (P0, P1, ...),
#   keywords, notes (short, own words), sources, llms_txt (optional link; omit when none).
# Each source: url (https, allowed host in index.yaml), title, kind, publisher, version,
#   primary (at least one true per concept), checked (date the link was last verified).
# Kinds: official-docs, api-reference, man-page, spec, project-repo.
"""


class LearnIndexError(Exception):
    """The learning index breaks a rule; `rule` names it and `where` says where."""

    def __init__(self, rule: str, where: str) -> None:
        """Store the rule name and the place for the message."""
        super().__init__(f"{where}: {rule}")
        self.rule, self.where = rule, where


class Source(BaseModel):
    """One official source for a concept."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    url: str
    title: str
    kind: SourceKind
    publisher: str
    version: str
    primary: bool = False
    checked: date


class Concept(BaseModel):
    """One concept that a guided story needs, with notes and sources."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    title: str
    area: Area
    stories: list[str]
    phase: str
    keywords: list[str] = []
    notes: str
    sources: list[Source]
    llms_txt: str | None = None

    @model_validator(mode="after")
    def check_concept(self) -> "Concept":
        """Require a matching id prefix and at least one primary source.

        Functional: Rejects a concept in the wrong area or without a primary source.
        Technical: Raises ValueError, which Pydantic turns into a ValidationError.
        """
        if not self.id.startswith(f"{self.area}."):
            msg = f"{self.id}: the id must start with '{self.area}.'"
            raise ValueError(msg)
        if not any(s.primary for s in self.sources):
            msg = f"{self.id}: at least one source must be primary"
            raise ValueError(msg)
        return self


class LearnIndex(BaseModel):
    """The whole learning index: settings plus every concept."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: int
    stale_after_days: int
    allowed_domains: list[str]
    concepts: list[Concept]


# ---------------------------------------------------------------- rules


def concept_urls(concept: Concept) -> list[str]:
    """Return every URL of a concept: its sources and its llms.txt link."""
    return [s.url for s in concept.sources] + ([concept.llms_txt] if concept.llms_txt else [])


def validate_index(index: LearnIndex) -> list[str]:
    """Return rule violations: repeated ids, non-https links, and hosts not allowed.

    Functional: Lists every problem so a person can fix them in one pass.
    Technical: Parses each URL with `urlparse`; counts ids in one pass.
    """
    problems: list[str] = []
    seen: set[str] = set()
    allowed = set(index.allowed_domains)
    for concept in index.concepts:
        if concept.id in seen:
            problems.append(f"{concept.id}: id repeats")
        seen.add(concept.id)
        for url in concept_urls(concept):
            parts = urlparse(url)
            if parts.scheme != "https":
                problems.append(f"{concept.id}: {url} does not use https")
            elif (parts.hostname or "") not in allowed:
                problems.append(f"{concept.id}: host {parts.hostname} is not allowed")
    return problems


def stale_warnings(index: LearnIndex, today: date) -> list[str]:
    """Return a warning for each source that was checked too long ago."""
    limit = index.stale_after_days
    return [
        f"{c.id}: source {s.url} is stale"
        for c in index.concepts
        for s in c.sources
        if (today - s.checked).days > limit
    ]


# ---------------------------------------------------------------- storage


class CanonicalDumper(yaml.SafeDumper):
    """YAML dumper that writes multi-line strings as literal blocks."""


def _represent_str(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    """Write a string with `|` when it has line breaks, else in the plain style."""
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


CanonicalDumper.add_representer(str, _represent_str)


def _to_yaml(data: YamlData) -> str:
    """Return data as canonical YAML text."""
    return yaml.dump(data, Dumper=CanonicalDumper, sort_keys=False, allow_unicode=True, width=1000)


def _read_area(path: Path) -> list[YamlData]:
    """Read one area file and add the area from its file name to each entry.

    Functional: Fails when the file is not a list or an entry states its own area.
    Errors: LearnIndexError (rule "list-of-concepts" or "area-from-file-name").
    """
    entries = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(entries, list):
        msg = "the file must be a list of concepts"
        raise LearnIndexError(msg, path.name)
    out = []
    for entry in entries:
        if isinstance(entry, dict) and "area" in entry:
            msg = "entries have no area key (the file name gives it)"
            raise LearnIndexError(msg, path.name)
        out.append({**entry, "area": path.stem} if isinstance(entry, dict) else entry)
    return out


def load_index(learn_dir: Path) -> LearnIndex:
    """Load index.yaml and every concepts/<area>.yaml, then validate them as one index.

    Functional: Returns the whole index, or fails on a file, schema, or concept rule error.
    Technical: Reads the area files in AREAS order; Pydantic validates the result.
    Errors: LearnIndexError (bad file layout), pydantic.ValidationError (schema or concept rule).
    """
    settings = yaml.safe_load((learn_dir / SETTINGS_NAME).read_text(encoding="utf-8")) or {}
    if not isinstance(settings, dict) or "concepts" in settings:
        msg = "the file holds settings only, no concepts"
        raise LearnIndexError(msg, SETTINGS_NAME)
    files = {p.stem: p for p in (learn_dir / CONCEPTS_DIR).glob("*.yaml")}
    unknown = sorted(set(files) - set(AREAS))
    if unknown:
        msg = f"unknown area; use one of {', '.join(AREAS)}"
        raise LearnIndexError(msg, f"{unknown[0]}.yaml")
    concepts = [c for area in AREAS if area in files for c in _read_area(files[area])]
    return LearnIndex.model_validate({**settings, "concepts": concepts})


def dump_index(index: LearnIndex) -> dict[str, str]:
    """Return the canonical text of every file, keyed by path relative to the learn dir.

    Functional: Same data gives the same text, with the fixed header comment on top.
    Technical: Drops `area` and an empty `llms_txt` from entries; an area without concepts
        gets no file.
    """
    data = index.model_dump()
    concepts = [
        {k: v for k, v in c.items() if not (k == "llms_txt" and v is None)}
        for c in data.pop("concepts")
    ]
    files = {SETTINGS_NAME: SETTINGS_HEADER + _to_yaml(data)}
    for area in AREAS:
        entries = [
            {k: v for k, v in c.items() if k != "area"} for c in concepts if c["area"] == area
        ]
        if entries:
            files[f"{CONCEPTS_DIR}/{area}.yaml"] = AREA_HEADER.format(area=area) + _to_yaml(entries)
    return files


def index_tag(learn_dir: Path) -> str:
    """Return a SHA-256 tag over the names and bytes of every index file."""
    digest = hashlib.sha256()
    for path in [learn_dir / SETTINGS_NAME, *sorted((learn_dir / CONCEPTS_DIR).glob("*.yaml"))]:
        digest.update(path.name.encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


def save_index(learn_dir: Path, index: LearnIndex) -> None:
    """Write every index file atomically and remove area files that are now empty.

    Technical: Temporary file next to each target, then `os.replace`.
    Limits: Files are replaced one by one, not as one transaction.
    """
    files = dump_index(index)
    for rel, text in files.items():
        temp = (learn_dir / rel).with_suffix(".yaml.tmp")
        temp.write_text(text, encoding="utf-8")
        os.replace(temp, learn_dir / rel)
    for area in AREAS:
        path = learn_dir / CONCEPTS_DIR / f"{area}.yaml"
        if f"{CONCEPTS_DIR}/{area}.yaml" not in files and path.exists():
            path.unlink()


# ---------------------------------------------------------------- check commands


def check_offline(learn_dir: Path) -> int:
    """Check the index offline and return the exit code (0 pass, 1 fail).

    Functional: Fails on a layout, schema, link, or id problem; warns on stale sources.
    """
    try:
        index = load_index(learn_dir)
    except (LearnIndexError, ValidationError) as error:
        print(f"FAIL {error}")
        return 1
    for warning in stale_warnings(index, datetime.now(UTC).date()):
        print(f"WARN {warning}")
    problems = validate_index(index)
    for problem in problems:
        print(f"FAIL {problem}")
    print(f"{len(index.concepts)} concepts checked.")
    return 1 if problems else 0


def url_is_alive(url: str) -> bool:
    """Return True when the URL answers HEAD or GET without an error.

    Technical: HEAD first, then GET; a URL error, timeout, or malformed URL is a failed try.
    Limits: 10 s per request; at most 2 requests per URL.
    """
    for method in ("HEAD", "GET"):
        try:
            headers = {"User-Agent": "cerberus"}
            request = urllib.request.Request(url, method=method, headers=headers)  # noqa: S310
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS):  # noqa: S310
                return True
        except (urllib.error.URLError, TimeoutError, ValueError):
            continue
    return False


def check_online(learn_dir: Path) -> int:
    """Run the offline check, then request every source and llms.txt URL once."""
    if check_offline(learn_dir) != 0:
        return 1
    index = load_index(learn_dir)
    urls = sorted({u for c in index.concepts for u in concept_urls(c)})
    dead = [u for u in urls if not url_is_alive(u)]
    for url in dead:
        print(f"FAIL dead link {url}")
    print(f"{len(urls)} links checked, {len(dead)} dead.")
    return 1 if dead else 0


# ---------------------------------------------------------------- editor server


class EditorHandler(BaseHTTPRequestHandler):
    """HTTP handler: GET / (page), GET /api/index (data), PUT /api/index (save)."""

    learn_dir: Path = LEARN_DIR

    def log_message(self, format: str, *args: object) -> None:
        """Keep the console quiet; the page shows the results."""

    def _send(self, status: int, body: bytes, kind: str = "application/json") -> None:
        """Send one response with a content type and no caching."""
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, data: YamlData) -> None:
        """Send a JSON response."""
        self._send(status, json.dumps(data).encode())

    def _host_ok(self) -> bool:
        """Accept only local Host headers, which blocks DNS rebinding."""
        return self.headers.get("Host", "") in {f"{HOST}:{PORT}", f"localhost:{PORT}"}

    def do_GET(self) -> None:
        """Serve the page or the index data with its tag and stale warnings."""
        if not self._host_ok():
            return self._json(HTTPStatus.FORBIDDEN, {"problems": ["The Host header is not local."]})
        if self.path == "/":
            return self._send(HTTPStatus.OK, PAGE.encode(), "text/html; charset=utf-8")
        if self.path != "/api/index":
            return self._json(HTTPStatus.NOT_FOUND, {"problems": ["Not found."]})
        try:
            index = load_index(self.learn_dir)
        except (LearnIndexError, ValidationError) as error:
            return self._json(HTTPStatus.UNPROCESSABLE_ENTITY, {"problems": [str(error)]})
        warnings = stale_warnings(index, datetime.now(UTC).date())
        data = {"tag": index_tag(self.learn_dir), "warnings": warnings}
        return self._json(HTTPStatus.OK, data | {"index": index.model_dump(mode="json")})

    def do_PUT(self) -> None:
        """Save the index when the If-Match tag is current and every rule passes.

        Functional: Writes nothing on an old tag (409) or a rule failure (422).
        Technical: JSON body only, at most 5 MB; cross-site pages cannot send it without
            a CORS preflight, which this server never allows.
        """
        length = int(self.headers.get("Content-Length") or 0)
        if not self._host_ok() or self.path != "/api/index" or length > MAX_BODY_BYTES:
            return self._json(HTTPStatus.FORBIDDEN, {"problems": ["The request is not allowed."]})
        if "application/json" not in self.headers.get("Content-Type", ""):
            return self._json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"problems": ["Send JSON."]})
        if self.headers.get("If-Match", "") != index_tag(self.learn_dir):
            msg = "The index files change after you load them. Load them again."
            return self._json(HTTPStatus.CONFLICT, {"problems": [msg]})
        try:
            index = LearnIndex.model_validate_json(self.rfile.read(length))
        except ValidationError as error:
            lines = [f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in error.errors()]
            return self._json(HTTPStatus.UNPROCESSABLE_ENTITY, {"problems": lines})
        problems = validate_index(index)
        if problems:
            return self._json(HTTPStatus.UNPROCESSABLE_ENTITY, {"problems": problems})
        save_index(self.learn_dir, index)
        return self._json(HTTPStatus.OK, {"tag": index_tag(self.learn_dir)})


def edit(learn_dir: Path) -> int:
    """Serve the editor on http://127.0.0.1:8765 until Ctrl+C."""
    EditorHandler.learn_dir = learn_dir
    server = ThreadingHTTPServer((HOST, PORT), EditorHandler)
    print(f"The editor runs at http://{HOST}:{PORT}. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("The editor stops.")
    return 0


def main(argv: list[str]) -> int:
    """Run the command in argv and return the exit code (2 for a usage error)."""
    commands = {
        ("check",): check_offline,
        ("check", "--online"): check_online,
        ("edit",): edit,
    }
    command = commands.get(tuple(argv[1:]))
    if command is None:
        print(USAGE)
        return 2
    return command(LEARN_DIR)


# ---------------------------------------------------------------- editor page

PAGE = r"""<!doctype html>
<!-- Editor page for the learning index. Served by docs/learn/learn.py edit. No external scripts. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Learning Index</title>
<style>
  :root {
    --bg: #f7f7f5; --panel: #ffffff; --text: #1d1d1b; --muted: #6b6b66; --line: #deded8;
    --accent: #2f5fd0; --danger: #b3261e; --ok: #1e7a3c; --warn: #9a6200; --chip: #eef1f8;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #161615; --panel: #1f1f1d; --text: #ecece8; --muted: #a2a29a; --line: #34342f;
      --accent: #7ea2ff; --danger: #ff8a80; --ok: #6fcf8e; --warn: #f0b75a; --chip: #262b38;
    }
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--text);
         font: 14px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; }
  header { position: sticky; top: 0; z-index: 2; display: flex; flex-wrap: wrap; gap: 8px;
           align-items: center; padding: 10px 16px; background: var(--panel);
           border-bottom: 1px solid var(--line); }
  header h1 { font-size: 16px; margin: 0 12px 0 0; }
  input, select, textarea, button { font: inherit; color: inherit; }
  input, select, textarea { background: var(--bg); border: 1px solid var(--line);
                            border-radius: 6px; padding: 5px 8px; width: 100%; }
  textarea { resize: vertical; }
  button { border: 1px solid var(--line); background: var(--panel); border-radius: 6px;
           padding: 5px 12px; cursor: pointer; }
  button.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
  button.danger { color: var(--danger); }
  button:disabled { opacity: .5; cursor: default; }
  #search { width: 240px; } #areaFilter { width: auto; }
  #status { margin-left: auto; color: var(--muted); }
  main { display: grid; grid-template-columns: 320px 1fr; gap: 16px; padding: 16px; }
  @media (max-width: 760px) { main { grid-template-columns: 1fr; } #search { width: 100%; } }
  .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; }
  #list { max-height: calc(100vh - 120px); overflow: auto; }
  #list .item { padding: 8px 12px; border-bottom: 1px solid var(--line); cursor: pointer; }
  #list .item:hover { background: var(--chip); }
  #list .item.active { border-left: 3px solid var(--accent); background: var(--chip); }
  #list .id { font-family: ui-monospace, monospace; font-size: 12px; color: var(--muted); }
  #editor { padding: 16px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
  label { display: block; font-size: 12px; color: var(--muted); margin: 10px 0 3px; }
  .source { border: 1px solid var(--line); border-radius: 6px; padding: 8px 10px; margin-top: 8px; }
  .row { display: flex; gap: 8px; align-items: center; margin-top: 10px; flex-wrap: wrap; }
  .chip { display: inline-block; background: var(--chip); border-radius: 10px; padding: 0 8px;
          font-size: 12px; margin-right: 4px; }
  #messages { margin: 0 16px; }
  #messages div { padding: 8px 12px; border-radius: 6px; margin-top: 8px; white-space: pre-wrap; }
  .msg-error { background: color-mix(in srgb, var(--danger) 14%, transparent); }
  .msg-ok { background: color-mix(in srgb, var(--ok) 14%, transparent); }
  .msg-warn { background: color-mix(in srgb, var(--warn) 14%, transparent); }
  details { margin-top: 16px; }
  a { color: var(--accent); }
</style>
</head>
<body>
<header>
  <h1>Learning index</h1>
  <input id="search" type="search" placeholder="Search id, title, keyword, notes">
  <select id="areaFilter"><option value="">All areas</option></select>
  <button id="newBtn">New concept</button>
  <button id="saveBtn" class="primary" disabled>Save</button>
  <span id="status">Loading…</span>
</header>
<div id="messages"></div>
<main>
  <div id="list" class="panel"></div>
  <div id="editor" class="panel"><p>Select a concept.</p></div>
</main>
<script>
"use strict";
const AREAS = ["sandbox", "realtime", "persistence", "security", "protocol", "build"];
const KINDS = ["official-docs", "api-reference", "man-page", "spec", "project-repo"];
const state = { data: null, tag: "", selected: -1, dirty: false };
const $ = (id) => document.getElementById(id);

/** Create an element with properties and children. */
function el(tag, props = {}, ...children) {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children.filter((c) => c !== null && c !== undefined));
  return node;
}

/** Show messages above the page.
 * Functional: Replaces old messages; kind is "error", "ok", or "warn".
 */
function say(kind, lines) {
  $("messages").replaceChildren(...lines.map((t) => el("div", { className: `msg-${kind}`, textContent: t })));
}

/** Mark the data as changed or saved and update the Save button. */
function setDirty(value) {
  state.dirty = value;
  $("saveBtn").disabled = !value;
  $("status").textContent = value ? "Unsaved changes" : `${state.data.concepts.length} concepts`;
}

/** Load the index from the server.
 * Functional: Shows stale-source warnings; keeps the version tag for the next save.
 */
async function load() {
  const res = await fetch("/api/index");
  if (!res.ok) { say("error", [`Load failed (${res.status}).`, await res.text()]); return; }
  const body = await res.json();
  state.data = body.index;
  state.tag = body.tag;
  say("warn", body.warnings.length ? [`${body.warnings.length} stale sources:`, ...body.warnings] : []);
  if (!body.warnings.length) $("messages").replaceChildren();
  setDirty(false);
  renderList();
  renderEditor();
}

/** Save the whole index to the server.
 * Functional: Shows each rule problem on failure; on a 409 asks the user to reload.
 * Technical: PUT /api/index with If-Match set to the last version tag.
 */
async function save() {
  const res = await fetch("/api/index", {
    method: "PUT",
    headers: { "Content-Type": "application/json", "If-Match": state.tag },
    body: JSON.stringify(state.data),
  });
  const body = await res.json();
  if (res.ok) { state.tag = body.tag; setDirty(false); say("ok", ["Saved."]); renderList(); return; }
  const lines = body.problems || (body.detail || []).map((d) => `${d.loc.join(".")}: ${d.msg}`);
  say("error", [`Save failed (${res.status}). Nothing is written.`, ...lines]);
}

/** Return true when a concept matches the search text and area filter. */
function matches(c, text, area) {
  if (area && c.area !== area) return false;
  const hay = [c.id, c.title, c.notes, ...c.keywords, ...c.stories].join(" ").toLowerCase();
  return hay.includes(text);
}

/** Render the concept list with the current search and filter. */
function renderList() {
  const text = $("search").value.trim().toLowerCase();
  const area = $("areaFilter").value;
  const items = state.data.concepts
    .map((c, i) => [c, i])
    .filter(([c]) => matches(c, text, area))
    .map(([c, i]) => {
      const item = el("div", { className: "item" + (i === state.selected ? " active" : "") },
        el("div", { textContent: c.title }),
        el("div", { className: "id", textContent: `${c.id} · ${c.stories.join(", ")}` }));
      item.onclick = () => { state.selected = i; renderList(); renderEditor(); };
      return item;
    });
  $("list").replaceChildren(...items);
}

/** Create a labeled input bound to a field of obj.
 * Functional: Edits write straight into the data and mark it unsaved.
 * Technical: kind "list" maps a comma-separated string to an array; "null" maps "" to null.
 */
function field(label, obj, key, kind = "text", options = null) {
  let input;
  if (options) {
    input = el("select", {}, ...options.map((o) => el("option", { value: o, textContent: o })));
  } else if (kind === "area") {
    input = el("textarea", { rows: 6 });
  } else {
    input = el("input", { type: kind === "date" ? "date" : kind === "bool" ? "checkbox" : "text" });
  }
  const value = obj[key];
  if (kind === "bool") input.checked = value; else
    input.value = kind === "list" ? value.join(", ") : value ?? "";
  input.oninput = input.onchange = () => {
    if (kind === "bool") obj[key] = input.checked;
    else if (kind === "list") obj[key] = input.value.split(",").map((s) => s.trim()).filter(Boolean);
    else if (kind === "null") obj[key] = input.value.trim() || null;
    else obj[key] = input.value;
    setDirty(true);
    if (key === "title" || key === "id") renderList();
  };
  if (kind === "bool") input.style.width = "auto";
  return el("div", {}, el("label", { textContent: label }), input);
}

/** Render one source row with its fields and a remove button. */
function renderSource(concept, s, idx) {
  const remove = el("button", { className: "danger", textContent: "Remove source" });
  remove.onclick = () => { concept.sources.splice(idx, 1); setDirty(true); renderEditor(); };
  const link = el("a", { href: s.url, target: "_blank", rel: "noopener", textContent: "Open link" });
  return el("div", { className: "source" },
    field("URL (https, allowed host)", s, "url"),
    el("div", { className: "grid" },
      field("Title", s, "title"), field("Kind", s, "kind", "text", KINDS),
      field("Publisher", s, "publisher"), field("Version", s, "version"),
      field("Checked", s, "checked", "date"), field("Primary", s, "primary", "bool")),
    el("div", { className: "row" }, link, remove));
}

/** Render the form for the selected concept, plus the file settings. */
function renderEditor() {
  const box = $("editor");
  const c = state.data.concepts[state.selected];
  const settings = renderSettings();
  if (!c) { box.replaceChildren(el("p", { textContent: "Select a concept." }), settings); return; }
  const addSource = el("button", { textContent: "Add source" });
  addSource.onclick = () => {
    c.sources.push({ url: "https://", title: "", kind: "official-docs", publisher: "",
                     version: "", primary: c.sources.length === 0, checked: today() });
    setDirty(true); renderEditor();
  };
  const del = el("button", { className: "danger", textContent: "Delete concept" });
  del.onclick = () => {
    if (!confirm(`Delete ${c.id}?`)) return;
    state.data.concepts.splice(state.selected, 1);
    state.selected = -1; setDirty(true); renderList(); renderEditor();
  };
  box.replaceChildren(
    el("div", { className: "grid" },
      field("Id (area.name)", c, "id"), field("Title", c, "title"),
      field("Area", c, "area", "text", AREAS), field("Phase", c, "phase"),
      field("Stories (comma)", c, "stories", "list"), field("Keywords (comma)", c, "keywords", "list")),
    field("Notes (own words)", c, "notes", "area"),
    field("llms.txt URL (optional)", c, "llms_txt", "null"),
    el("h3", { textContent: `Sources (${c.sources.length})` }),
    ...c.sources.map((s, i) => renderSource(c, s, i)),
    el("div", { className: "row" }, addSource, del),
    settings);
}

/** Render the file-level settings: allowed domains and stale days. */
function renderSettings() {
  const d = state.data;
  const domains = el("textarea", { rows: 8, value: d.allowed_domains.join("\n") });
  domains.oninput = () => {
    d.allowed_domains = domains.value.split("\n").map((s) => s.trim()).filter(Boolean);
    setDirty(true);
  };
  const stale = el("input", { type: "number", min: 1, value: d.stale_after_days });
  stale.oninput = () => { d.stale_after_days = Number(stale.value); setDirty(true); };
  return el("details", {},
    el("summary", { textContent: `File settings (${d.allowed_domains.length} allowed domains)` }),
    el("label", { textContent: "Allowed domains (one per line)" }), domains,
    el("label", { textContent: "Stale after days" }), stale);
}

/** Return today's date as YYYY-MM-DD. */
function today() { return new Date().toISOString().slice(0, 10); }

/** Add a new concept in the current area filter and select it. */
function newConcept() {
  const area = $("areaFilter").value || "sandbox";
  state.data.concepts.push({ id: `${area}.new-concept`, title: "New concept", area,
    stories: [], phase: "P1", keywords: [], notes: "", sources: [], llms_txt: null });
  state.selected = state.data.concepts.length - 1;
  $("search").value = "";
  setDirty(true); renderList(); renderEditor();
}

AREAS.forEach((a) => $("areaFilter").append(el("option", { value: a, textContent: a })));
$("search").oninput = renderList;
$("areaFilter").onchange = renderList;
$("newBtn").onclick = newConcept;
$("saveBtn").onclick = save;
window.onbeforeunload = (e) => { if (state.dirty) { e.preventDefault(); return ""; } };
load();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
