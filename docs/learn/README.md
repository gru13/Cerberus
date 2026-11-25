# Learning index

The learning index is a set of YAML files and is its own source of truth. Each concept has short
notes in our own words and official sources. There are no generated pages.

| File | Holds |
|---|---|
| `index.yaml` | Settings: `version`, `stale_after_days`, `allowed_domains`. No concepts. |
| `concepts/<area>.yaml` | The concepts of one area, as a list. The file name gives the area, so entries have no `area` key. Areas: sandbox, realtime, persistence, security, protocol, build. |
| `learn.py` | The one tool: check, link check, and the browser editor (single file, standalone). |
| `guided-study-guide.md` | The study guide that lists the concepts each guided story needs. |

Each YAML file starts with a comment that explains its fields.

- Cite a concept by its id, for example `sandbox.openat2` (in `concepts/sandbox.yaml`).
- Policy: official sources only, https only, on the `allowed_domains` in `index.yaml`.
- Every concept has at least one primary source.

## Commands

`learn.py` declares its own dependencies (pydantic, pyyaml), so `uv run` needs no setup.

| Task | Command | What it does |
|---|---|---|
| `learn: check` | `uv run docs/learn/learn.py check` | Checks layout, schema, ids, https, allowed hosts, and primary sources. CI runs it. |
| `learn: check-links` | `uv run docs/learn/learn.py check --online` | Runs the check, then requests every link. Run it on your own machine. |
| `learn: edit` | `uv run docs/learn/learn.py edit` | Opens a local editor at http://127.0.0.1:8765: browse, search, add, change, and delete concepts. |

The editor checks every save with the same rules and writes nothing when a rule fails. It refuses
a save when any index file changed after the page loaded it, so a hand edit is never lost. It
accepts only local requests. Hand edits to the YAML are fine too.

## Known gaps

- `protocol.pydantic-discriminated-unions` cites the Pydantic GitHub docs, because
  docs.pydantic.dev redirects to pydantic.dev, which is not an allowed host.
- `protocol.serde-tagged-enums` cites serde-rs.github.io, because serde.rs is not an allowed host.
- `security.dns-rebinding` is partial: no official page covers it on an allowed host, so it cites
  the OWASP SSRF sheet and Starlette TrustedHost.
- Starlette is cited on starlette.dev; www.starlette.io did not resolve when the index was built.
