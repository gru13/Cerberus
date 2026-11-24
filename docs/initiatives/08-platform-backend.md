**Level:** Initiative 8 (issue #190) · **Status:** Designed

**Purpose:** The shared backend that every initiative builds on. One FastAPI app (Python), one Postgres database, one job queue, one realtime relay, one logger.

**Split rule:** #190 owns `api/src/cerberus/platform/` and run orchestration (`api/src/cerberus/runs/`). Each initiative owns its own endpoints and tables, built on #190.
**Builds on:** decision 0001, `docs/architecture.md`.
**Used by:** #1 (API, TypeScript client, realtime), #2, #3, #4, #5, #6, #7.

## Key design points

1. **One codebase, two processes.** `cerberus api` serves HTTP and WebSocket. `cerberus worker` runs long jobs (builds, validations, test runs, generation). Same image, different command.
2. **Postgres is the only infrastructure.** Data, job queue (procrastinate, `SKIP LOCKED`), and cross-process events (`LISTEN/NOTIFY` behind `EventBus`). No Redis, no Kafka. Terminals go browser -> Caddy -> agent; the API only issues terminal tokens (8.4.3, 8.7.4).
3. **Logs and events are different.** Logs are operational (stdout + file). Events are domain facts in the `events` table for replay and the knowledge graph. Both use STE100 and the subject-predicate-object triple.
4. **Local is still protected.** Any website can call `localhost`, so the API checks Host and Origin, uses a SameSite=Strict cookie, and needs a CSRF token on writes.


## Epic 8.1 — App skeleton and config

Project setup, config, errors, health, and local security.

| Story | Description | Done when |
|---|---|---|
| 8.1.1 Project setup | `api/` with Python 3.13, uv, FastAPI, ruff, ty (type checker), pytest. `cerberus` CLI: `api`, `worker`, `migrate`, `doctor`. CI workflow `ci-api`. | A hello endpoint works; CI passes. |
| 8.1.2 Config | Deploy config from env with pydantic-settings (`CERBERUS_MODE`, DB URL, data dir). User settings in the DB. | A bad config stops start with a clear STE100 message. |
| 8.1.3 Error format | problem+json (RFC 9457), error code registry, request id. | All errors have the same shape. |
| 8.1.4 Health | `/healthz` (live) and `/readyz` (DB, Docker, free disk, data dir writable). | The UI status page uses them. |
| 8.1.5 Local security `guided` | Host and Origin allow-list (blocks DNS rebinding), SameSite=Strict session cookie, CSRF check on writes, API bound to 127.0.0.1 only. | A request from another origin is rejected. |

## Epic 8.2 — Database and migrations

Async SQLAlchemy, tenancy, Alembic, core tables, backup.

| Story | Description | Done when |
|---|---|---|
| 8.2.1 Database setup | Async SQLAlchemy 2 + asyncpg. Base model: `id` (UUIDv7), `org_id`, `user_id`, timestamps. | Models work in tests. |
| 8.2.2 Tenancy guard `guided` | Queries are scoped by org and user automatically. A test fails if a table has no `org_id`. | One user cannot read the rows of another user. |
| 8.2.3 Migrations | Alembic; run on start (`cerberus migrate`). CI checks the migration chain and that models match. | A fresh DB and an upgraded DB are the same. |
| 8.2.4 Core tables | `orgs`, `users`, `memberships` (roles), `settings`. Local mode seeds org `local` and user `local` with all roles. | First start creates the local user. |
| 8.2.5 Backup and restore | `cerberus backup` (pg_dump + host store) and `cerberus restore`. | Restore on a clean machine works. |

## Epic 8.3 — Provider factories

One factory builds every decision-0001 provider.

| Story | Description | Done when |
|---|---|---|
| 8.3.1 Factory | One module reads `CERBERUS_MODE` and builds all providers; injected with FastAPI `Depends`. A test fails if mode checks appear anywhere else. | The mode is read in one place. |
| 8.3.2 AuthProvider and roles | `LocalAuth` (implicit local user); `require_role(...)` dependency. `OidcAuth` parked. | Role checks work on endpoints. |
| 8.3.3 KeyProvider | `UserKey` from the encrypted store (8.7). `OrgKey` parked. | The tutor gets a key without seeing storage. |
| 8.3.4 BlobStore | New interface: `LocalFolder` now, `ObjectStorage` parked. Used by the host store and snapshots. | Same code in both modes. |
| 8.3.5 Other interfaces | Protocols for `ImageProvider`, `SandboxExecutor`, `ContentSource`; implementations live in #2 and #4. | #2 and #4 plug in without platform changes. |

## Epic 8.4 — Realtime relay

Browser socket, agent connections, terminal streams, and the EventBus.

| Story | Description | Done when |
|---|---|---|
| 8.4.1 Browser socket `guided` | One WebSocket per tab (`/api/v1/ws`), channels: terminal, files, ports, tasks, toasts. Cookie auth, heartbeat, resume from last event id. | A reconnect loses no events. |
| 8.4.2 Agent connections `guided` | One Unix-socket connection per session; reconnect with backoff; protocol version check. | An agent restart reconnects. |
| 8.4.3 Terminal streams `guided` | The terminal goes direct: browser -> Caddy -> agent WebSocket. The backend only issues a terminal token (8.7.4) and logs session start and stop. Binary frames both ways, resize messages, backpressure. | Typing latency < 30 ms locally; the backend carries no terminal bytes. |
| 8.4.4 EventBus interface and PostgresBus `guided` | `EventBus` publish/subscribe interface. `PostgresBus` (LISTEN/NOTIFY) now; `NatsBus` parked for hosted. No Kafka. | Worker events reach the browser through the EventBus. |

## Epic 8.5 — Job queue

Postgres job queue (procrastinate) in a separate worker process.

| Story | Description | Done when |
|---|---|---|
| 8.5.1 Queue on Postgres | procrastinate on Postgres (`SKIP LOCKED`), priorities, `run_at`; separate `cerberus worker` process from the same image. | Jobs run in the worker. |
| 8.5.2 Retries and leases `guided` | Lease with heartbeat; expired lease goes back to the queue; max attempts; idempotency key; dead-letter list. | Killing the worker loses no job. |
| 8.5.3 Concurrency limits | Per job type. Local: 1 test run (#4.6.3), 1 build, 1 generation. | Limits are enforced. |
| 8.5.4 Progress and cancel | Jobs send progress through the EventBus (startup steps, build logs); cancel. | The UI shows live progress. |
| 8.5.5 Scheduled jobs | Idle check (30 min), cleanup, pool pre-fill (#3). | Periodic jobs run. |

## Epic 8.6 — Events and logging

STE100 logger, event registry, event store, traces, graph export.

| Story | Description | Done when |
|---|---|---|
| 8.6.1 STE100 logger | structlog JSON lines to stdout and `~/.cerberus/logs/` (rotating); required CLAUDE.md fields; secret redaction filter. | Every line has the triple and a `trace_id`. |
| 8.6.2 Event registry | Event names, entity types, and verbs in a code registry, checked against `docs/ontology.md` in CI. A `msg` over 20 words fails the test. | An unknown term fails CI. |
| 8.6.3 Event store | Append-only `events` table (triple, payload, `run_id`). Takes events from the agent and the browser. | Replay (#1.8.4, #6) reads from it. |
| 8.6.4 Trace ids | One trace id from browser request to API, job, and agent. | One id follows a full run start. |
| 8.6.5 Knowledge-graph export | `cerberus export-graph`: nodes and edges (CSV / JSON-LD) from events. | The graph opens in a graph tool. |

## Epic 8.7 — Secrets

Encryption at rest, API keys, rotation, and tokens.

| Story | Description | Done when |
|---|---|---|
| 8.7.1 Encryption at rest `guided` | AES-GCM. Master key created on first start in `~/.cerberus/secret.key` (0600) or from env; key id per record. | DB keys are unreadable without the master key. |
| 8.7.2 API key storage `guided` | Show only the last 4 characters; decrypt only on the tutor call path; redaction test on logs. | A key never appears in logs or responses. |
| 8.7.3 Key rotation | `cerberus rotate-key` encrypts all records again with a new key. | Rotation loses no key. |
| 8.7.4 Tokens `guided` | MCP, preview, and terminal tokens: random, stored hashed, scoped, expiring, revocable. Terminal tokens: signed, about 60 s to connect, bound to run and user, single use. | A revoked token fails at once; a terminal token works once only. |

## Epic 8.8 — Recovery and host store

Write-through host store, conflict checks, startup checks, and recovery.

| Story | Description | Done when |
|---|---|---|
| 8.8.1 Host store `guided` | Write-through on every save; blobs by sha256 in `~/.cerberus/runs/<run>/files/`; manifest table `run_files` (path, hash, version, source: editor or terminal). | Every saved edit is on disk. |
| 8.8.2 Terminal change capture `guided` | Agent file-watch events -> debounced fetch -> store. | A `sed -i` change reaches the store. |
| 8.8.3 Conflict check `guided` | Each save sends `base_hash`; a mismatch returns 409 with the server version (used by #1.4.3). | Journal replay never overwrites silently. |
| 8.8.4 Startup checks `guided` | Compare the DB with Docker: `ready` runs without a container become `interrupted`; clean orphans (#4.1.5); requeue expired leases. | A Docker restart leaves a consistent state. |
| 8.8.5 Recover endpoint `guided` | Fast path (reattach volume) or slow path (rebuild from store), with progress events. | #1.3.4 Recover works. |

## Epic 8.9 — API contract and clients

API conventions, generated TypeScript client, agent protocol codegen, contract tests.

| Story | Description | Done when |
|---|---|---|
| 8.9.1 API conventions | `/api/v1`, resource names, cursor pagination, stable operationIds. | Documented in `docs/`. |
| 8.9.2 TypeScript client | `openapi-typescript` + `openapi-fetch` generate `web/src/lib/api`; CI fails when it is out of date. | The web app compiles against the generated client. |
| 8.9.3 Agent protocol codegen `guided` | Pydantic models generated from `protocol/agent.v1.schema.json`. The Rust side tests sample messages against the schema (owner, guided). | Both sides pass the schema check in CI. |
| 8.9.4 Contract tests | Schemathesis fuzzes the OpenAPI spec in CI. | No 500 errors on fuzzed input. |
| 8.9.5 Fake agent for tests | A small Python test double that speaks `protocol/agent.v1.schema.json` (files, terminals, tasks, ports, events with canned data). The backend and UI build and test against it until the owner's Rust agent is ready. Not a replacement for the agent. | Backend and UI tests pass against the fake agent; swapping in the real agent needs no code change. |

## Epic 8.10 — Compose packaging

One-command local install with HTTPS, a Docker socket proxy, and release images.

| Story | Description | Done when |
|---|---|---|
| 8.10.1 Compose file | Services db, api, worker, web, caddy; healthchecks; `restart: unless-stopped`; volume `cerberus-pg`; bind mount `~/.cerberus`. | `docker compose up` starts everything. |
| 8.10.2 Docker socket proxy `guided` | api and worker reach Docker only through a socket proxy that allows the needed endpoints. | No raw Docker socket in app containers. |
| 8.10.3 Local HTTPS | Caddy: `cerberus.localhost`, `*.localhost` previews, MCP; local CA download (#1.11.4). | The browser trusts the certificates after one setup step. |
| 8.10.4 Agent binary bundling `guided` | CI builds musl amd64 and arm64 agent binaries; the api image carries both; the executor copies the right one. | The agent works on both architectures. |
| 8.10.5 First run | Migrate, seed the local user, create the secret key, print the URL. `cerberus doctor` checks the setup. | A new user runs Cerberus in < 5 minutes. |
| 8.10.6 Release images | api and web images on GHCR on each tag; compose pulls them. Local build for development. | Users need no build tools. |

## Epic 8.11 — Run orchestration

The run state machine that connects #3 (issue), #4 (session), and #6 (grading).

| Story | Description | Done when |
|---|---|---|
| 8.11.1 Run model and states | created -> preparing -> ready <-> interrupted -> submitted -> graded -> closed (or failed). `runs` table: user, project version, issue version, mode, times, score. | Every state change is logged. |
| 8.11.2 Start run | Pick issue (#3 service) -> create session (#4) -> ready; progress events; idempotent. | #1.3.1 starts a run. |
| 8.11.3 Submit run | Freeze a host store snapshot -> queue grading (#6) -> store the result. | #1.8.2 Submit works. |
| 8.11.4 Run lifecycle events | `run.start`, `run.edit`, `run.test`, `run.hint`, `run.submit`, `run.score`, `run.recover`, as in CLAUDE.md. | One full run is traceable from events. |

## Epic 8.12 — Hosted backend (parked)

Placeholders for hosted mode.

| Story | Description | Done when |
|---|---|---|
| 8.12.1 Scale-out - parked | Many API replicas, external Postgres, object storage, OIDC, `NatsBus`. | Placeholder. |
| 8.12.2 Rate limits and quotas - parked | Per user and per org. | Placeholder. |

## Order

```
8.1.1-8.1.4 -> 8.2.1-8.2.4 -> 8.3.1-8.3.2 -> 8.6.1 -> 8.10.1 + 8.10.3   (stack starts)
-> 8.9.1-8.9.2 -> 8.1.5 -> 8.4.1-8.4.4 (terminal relay, EventBus) -> 8.5.1-8.5.4
-> 8.8.1-8.8.3 -> 8.11.1-8.11.2 -> 8.7.1-8.7.2 -> 8.8.4-8.8.5 -> 8.11.3-8.11.4
-> 8.6.2-8.6.4 -> 8.3.3-8.3.5 -> 8.9.3-8.9.4 -> 8.10.2, 8.10.4-8.10.6 -> 8.5.5 -> 8.2.5 -> 8.7.3-8.7.4 -> 8.6.5
```

**First milestone:** `docker compose up` -> https://cerberus.localhost shows a health page -> migrations ran and the local user exists -> the generated TypeScript client calls `/readyz` -> the API writes an STE100 JSON log line.

## Decisions

- Run orchestration belongs to #190 (Epic 8.11). Each step stays with its owner (#3, #4, #6).
- Job queue: procrastinate on Postgres, in a separate worker process.
- No Kafka or other broker. `EventBus` interface: `PostgresBus` now, `NatsBus` for hosted later.
- Backend tooling: Python 3.13, uv, ruff, ty (backend only; content projects choose their own).
- Docker access through a socket proxy.
- Release images on GHCR; local build for development.
- Decision 0001 gets two new interfaces: `BlobStore` and `EventBus`.

## Log events

`platform.start|stop`, `platform.migrate`, `platform.recover.check`, `job.queue|start|done|fail|retry`, `secret.rotate`, `run.start|ready|interrupt|recover|submit|score|close`
