**Level:** Initiative · **Status:** Designed

**Purpose:** A growing library of correct, versioned projects in any stack. Cerberus syncs them, builds local Docker images, and registers each version in its database.

**Out of scope:** issues and patches (#3), patch apply and trace removal (#4), grading (#6), tutor tools and docs/RAG (#5).

See also: [0001 — Deployment modes](../decisions/0001-deployment-modes.md).

## Project contract

```
projects/<name>/
├── Dockerfile              # full environment, project-owned (no shared base)
├── .vscode/tasks.json      # required labels: run-project, run-tests
├── project.yaml            # platform metadata (editable allow-list etc.)
├── README.md               # what the app is, how to run
└── …any structure (source, tests, seed data)…
```

- Seed data is the project creator's responsibility.
- Tests are visible to the user and read-only.
- `run-tests` writes JUnit XML. The platform calls only `run-project` and `run-tests`.
- **Servers bind to `0.0.0.0`**, not `127.0.0.1`. The preview proxy reaches the container over the network.
- **Frontends call backends by a relative path** (`/api/...`) through the dev-server proxy (for example Vite `server.proxy`). Never `http://localhost:<port>`: in the browser, `localhost` is the user's machine, not the container.
- `project.yaml` `preview_port` (optional) names the main app port. The preview opens it automatically.
- `project.yaml` `grading_tests` (optional) lists held-out tests. The dev box does not have them; only grading runs them (#6).

---

## Epic 2.1 — Content repo

| Story | Description | Done when |
|---|---|---|
| 2.1.1 Create `cerberus-content` | Private repo (public at open-source release). Same safety rules: protected main, linked-issue check, hooks, CODEOWNERS, PR template | Push to main is rejected; PR without issue fails; fake key is blocked |
| 2.1.2 Repo layout | `projects/<name>/`, `projects/_template/`, `tools/validate/`, `tools/schema/`, `docs/`, `.github/workflows/validate.yml` | Layout is in the README |
| 2.1.3 Contributor guide and template | `CONTRIBUTING.md` step by step and a working `_template` project | A hello-world project is added with the guide only |

## Epic 2.2 — Project contract and validator

| Story | Description | Done when |
|---|---|---|
| 2.2.1 `project.yaml` schema | name, title, description, languages, **editable allow-list**, `readonly_extra` (optional), `test_report` glob, workdir, difficulty, tags, `preview_port` (optional), `grading_tests` (optional held-out test patterns, #6.1.2) | JSON Schema in `tools/schema/` |
| 2.2.2 `tasks.json` contract | Required labels **`run-project`** (compound allowed; no-op for libraries) and **`run-tests`** (JUnit XML, no network, ≤ 120 s, non-zero exit on failure). Prefix `cerberus-` is reserved. Other tasks are optional. Servers bind to `0.0.0.0`; frontends reach backends by relative path through the dev-server proxy | Validator enforces exact labels and the bind rule |
| 2.2.3 Dockerfile rules `guided` | Project-owned; deps installed at build time (offline run); non-root user; `patch`, `ls`, `grep`, `find`, `cat` present; `.dockerignore` excludes `.git`; base pinned by digest; image ≤ 2 GB (warn > 1 GB); no secrets | Validator checks each rule |
| 2.2.4 Default read-only patterns | Test files, test/build config, lock files, `Dockerfile`, `.vscode/**`, `project.yaml`, README. Editable = in `editable` and not read-only | List in `docs/project-contract.md` |
| 2.2.5 Validator CLI | Static: files, schema, tasks, Dockerfile rules, secrets. Dynamic: build; `run-tests` passes 100 % with `--network none`, same result 3 times; `run-project` opens a port in 30 s **on `0.0.0.0`** (skip for libraries); tools present; non-root. Warning on `localhost:<port>` or `127.0.0.1:<port>` URLs in frontend source. With `grading_tests`: `run-tests` passes with and without them, and its JUnit report includes them | `tools/validate projects/<name>` gives a pass/fail report with STE100 log lines |
| 2.2.6 PR validation in CI | `validate.yml` runs the validator on PRs that touch `projects/**` | A broken project cannot merge |

## Epic 2.3 — Sync, build, and register (`ImageProvider`)

| Story | Description | Done when |
|---|---|---|
| 2.3.1 Content sync | Fetch content repo(s) on app start and on "Sync". Git-diff since the last synced commit to find changed projects | Sync reports added and changed projects |
| 2.3.2 Local build (`LocalBuild`) | For each changed project: `docker build` (network at build only) → `run-tests` with `--network none` → keep image `cerberus-proj-<name>:<short-sha>`. One build at a time, progress in the UI | A synced project becomes a local image with passing tests |
| 2.3.3 Registry tables | `projects`, `project_versions`: `org_id`, version_no (auto +1), **commit_sha**, image id/digest, tasks, editable, test_count, test_runtime_s, status, built_at. Idempotent on commit | Same commit twice does not duplicate |
| 2.3.4 Version status | available / broken / deprecated. Nothing is deleted automatically | Status shows in the project list |
| 2.3.5 Image cleanup | Keep latest available + versions used by saved runs. "Free disk space" action | Disk use stays under control |
| 2.3.6 Re-validation trigger | Emit `project.version.build` so the issue engine (#3) re-validates issues | Event is logged |
| 2.3.7 Registry provider (`RegistryPull`) — **parked** | Hosted mode: CI builds, pushes to a registry, workers pull by digest | Placeholder until hosted mode |

## Epic 2.4 — Seed projects

| Story | Description | Done when |
|---|---|---|
| 2.4.1 Specs | `SPEC.md` per project: features, modules, size, bug areas | Specs approved |
| 2.4.2 A — `flask-notes` (Python) | Python 3.14, uv, Flask, Jinja, SQLAlchemy, SQLite. List, create, edit, delete, search, tags, dates, JSON API, health. ~600–800 lines, 40–60 pytest tests | Passes validator; builds and runs locally |
| 2.4.3 C — `shop-api` (Node) | Node 22, TypeScript, pnpm, Fastify/Express, vitest. Products, cart, orders, stock, discounts | Passes validator |
| 2.4.4 B — `taskboard` (full stack) | FastAPI + React/Vite. Boards, columns, cards, drag to move, labels, due dates. Compound `run-project`, pytest + vitest, several JUnit files. Vite proxies `/api` to the backend; `preview_port: 5173` | Passes validator; the app works in the preview with no CORS setup |

**Order:** 2.1.1 → 2.1.2 → 2.2.1–2.2.4 → 2.4.1 → 2.4.2 → 2.2.5–2.2.6 → 2.3.1–2.3.6 → 2.4.3 → 2.4.4 → 2.1.3

## Decisions

- Git monorepo `cerberus-content` is the source of truth.
- Each project owns its Dockerfile. No shared base image.
- `tasks.json` has two required labels: `run-project`, `run-tests`. Results are JUnit XML.
- Servers bind to `0.0.0.0`. Frontends call backends by relative path through the dev-server proxy.
- Versions are automatic: merge → build → register with commit SHA. Merge to main is the publish step.
- Registry is parked until hosted mode.
- Library-only projects are allowed. Image ≤ 2 GB. Tests: target 30 s, max 120 s.
- Outside contributors come later.
