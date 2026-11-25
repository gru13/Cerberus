# Learning index

The learning index is a set of YAML files and is its own single source of truth. Each concept
has short notes in our own words and official sources. There are no generated pages.

| File | Holds |
|---|---|
| `index.yaml` | Settings: `version`, `stale_after_days`, `allowed_domains`. No concepts. |
| `concepts/<area>.yaml` | The concepts of one area, as a list. The area comes from the file name, so entries have no `area` key. Areas: sandbox, realtime, persistence, security, protocol, build. |

- Cite a concept by its id, for example `sandbox.openat2` (in `concepts/sandbox.yaml`).
- Policy: official sources only, https only, on the `allowed_domains` in `index.yaml`.
- Every concept has at least one primary source.

## Tasks

| Task | What it does |
|---|---|
| `learn: check` | Checks the file offline: schema, ids, https, allowed hosts, primary source. CI runs it. |
| `learn: check-links` | Runs `learn: check`, then requests every link. Run it on your own machine. |
| `learn: edit` | Starts a local editor at http://127.0.0.1:8765 to browse, search, add, change, and delete concepts. |

The editor checks every save with the same rules as `learn: check` and writes nothing when a
rule fails. It refuses a save when any index file changed after the page loaded it (for example after
a hand edit), so no change is lost. Hand edits to the YAML are also fine.

## Other files

- `guided-study-guide.md`: the study guide that lists the concepts each guided story needs.
- `PROGRESS.md`: the checklist from the first build of this index.
