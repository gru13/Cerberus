# Architecture

One monorepo with three apps: `web/` (Next.js), `api/` (FastAPI), `agent/` (Rust). Local mode runs with `docker compose up` (services: db, api, worker, web, caddy, Docker socket proxy).

## Request path

```
Browser (web/)
  │  REST (generated TypeScript client) + one WebSocket
  ▼
Caddy (local HTTPS: app, *.localhost previews, MCP)
  ▼
API (api/, FastAPI) + worker  ── Postgres (data, job queue, EventBus; cerberus-pg volume)
  │  Unix socket, protocol/agent.v1.schema.json
  ▼
Agent (agent/, Rust) inside each dev box container
```

The browser never talks to a container directly.

## Repository layout

```
Cerberus/
├── CLAUDE.md · README.md · LICENSE
├── docker-compose.yml          # local mode: db + api + worker + web + caddy + socket proxy
├── .env.example                # placeholders only
├── .githooks/                  # pre-commit, pre-push
├── .github/                    # workflows (linked-issue, ci-web, ci-api, ci-agent), CODEOWNERS, PR template
├── docs/                       # decisions/, initiatives/, ontology.md, architecture.md
├── logs/build.jsonl
│
├── web/                        # #1 Next.js (TypeScript)
│   └── src/
│       ├── app/                # routes: /, projects/[id], runs/[runId], author, review, settings
│       ├── components/ui/      # shadcn components (owned by us)
│       ├── components/shell/   # top bar, sidebar, toasts
│       ├── features/           # one folder per epic: workspace, terminal, tasks,
│       │                       # tests-panel, preview, chat, author, review, runs, projects, settings
│       ├── lib/api/            # GENERATED from OpenAPI (do not edit)
│       ├── lib/ws/             # realtime socket
│       ├── lib/query/          # TanStack Query setup
│       └── stores/             # Zustand (layout, tabs, panels)
│
├── api/                        # FastAPI (Python), modular monolith
│   ├── pyproject.toml · alembic.ini
│   ├── migrations/             # Alembic
│   ├── src/cerberus/
│   │   ├── main.py · config.py
│   │   ├── runs/               # #190 run orchestration (state machine)
│   │   ├── platform/           # #190: db, providers, queue, realtime, events,
│   │   │                       #     logging (STE100), secrets, store, recovery
│   │   ├── projects/           # #2
│   │   ├── issues/             # #3 (includes mcp/)
│   │   ├── sandbox/            # #4 executor, workspace, testrun, preview proxy, agent client
│   │   ├── llm/                # #5 shared LLM layer: adapters, usage, budgets (used by tutor and issues)
│   │   ├── tutor/              # #5 context, tools, guardrails, hints, docs
│   │   ├── scoring/            # #6
│   │   └── accounts/           # #7
│   └── tests/
│
├── agent/                      # #4.3 Rust, guided (the owner writes it)
├── protocol/agent.v1.schema.json   # shared contract: api <-> agent
├── skills/                     # #3 MCP skill file
├── deploy/                     # api/web Dockerfiles, agent-build (musl amd64 + arm64), caddy/Caddyfile
└── scripts/
```

### Backend module shape

```
issues/
├── router.py      # FastAPI endpoints
├── schemas.py     # Pydantic request/response
├── models.py      # SQLAlchemy tables
├── service.py     # business logic
└── jobs.py        # queue jobs
```

Rules:
- A module may import `platform/`.
- A module calls another module only through its `service.py`, never its tables.
- `platform/` (#190) owns shared parts. Each initiative owns its own endpoints and tables.

### Agent protocol

`protocol/agent.v1.schema.json` defines every message. The owner writes the Rust serde types by hand against it. Python models are generated from it. CI checks that both sides match.

## Other repositories

```
cerberus-content/ (private)          cerberus-issues/ (public)
└── projects/<name>/                 └── issues/<project>/*.jsonl
    ├── Dockerfile · .dockerignore
    ├── .vscode/tasks.json  (run-project, run-tests)
    ├── project.yaml · README.md
    └── src/ · tests/
```

## Runtime data (not in git)

```
~/.cerberus/
├── content/                 # clone of cerberus-content
├── runs/<run_id>/files/     # host store: source of truth for learner work
├── snapshots/<run_id>/      # full snapshot on submit
└── certs/                   # local CA for HTTPS

Docker volumes:  cerberus-pg · cerberus-run-<run_id>

Inside a dev box:
/workspace                   # run volume, patched and locked
/opt/cerberus/agent          # Rust binary (copied in)
/opt/cerberus/clean          # authoring sessions only
/run/cerberus/agent.sock     # Unix socket to the API
```

## Work persistence

Learner work has three copies. Any one can fail without data loss.

| Layer | Where | Survives |
|---|---|---|
| Browser journal | IndexedDB, keyed by run, file, base hash | Refresh, network drop, API or Docker down |
| Host store | `~/.cerberus/runs/<run>/files/`, write-through, content-addressed | Container loss, volume loss, Docker reset |
| Run volume | `cerberus-run-<id>` | Container crash, Docker restart |

| Failure | Lost | Recovery |
|---|---|---|
| Browser refresh | Nothing | Journal replays |
| Network drop | Nothing | Offline badge, replay on reconnect |
| Container crash or OOM | Processes and terminals | New container on the same volume |
| API crash | At most ~1 s in flight (browser keeps it) | Compose restarts the API; browser replays |
| Docker down or reboot | Processes | Startup check marks runs interrupted; Recover reattaches the volume; journal replays |
| Volume lost | Nothing | Fresh container, patch, traces, restore from host store, lock |
| Host disk lost | Everything local | Out of scope locally; hosted mode uses object storage |

Terminal edits reach the host store through agent file-watch events. A base-hash conflict shows a diff (Keep mine / Keep server). Grading uses the host store.
