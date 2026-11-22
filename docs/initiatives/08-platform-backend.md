**Level:** Initiative 8 (issue #190) · **Status:** Backlog (plan next)

**Purpose:** The shared backend that every initiative builds on. One FastAPI app (Python), one database, one job queue, one realtime relay, one logger.

**Split rule:** #190 owns the shared platform (`api/src/cerberus/platform/`). Each initiative owns its own endpoints and tables (for example, #3 owns `/issues`), built on #190.

**Used by:** #1 (API, TypeScript client, realtime), #2, #3, #4, #5, #6, #7.

## Scope

| Shared piece | Notes |
|---|---|
| App skeleton and config | FastAPI, settings, error format |
| Database and migrations | SQLAlchemy + Alembic; `org_id` and `user_id` on every table |
| Provider factories | Decision 0001: Auth, Image, Sandbox, Key, Content |
| Realtime relay | WebSocket browser <-> agent: terminals, file events, ports, toasts |
| Job queue | Postgres-based, no Redis: builds, validations, test runs, generation |
| Events and logging | Event store for replay; STE100 JSON-line logger |
| Secrets | Encrypt API keys at rest |
| Recovery and host store | Startup check marks interrupted runs; write-through store for learner files |
| API contract | OpenAPI -> generated TypeScript client for `web/` |
| Compose packaging | `docker-compose.yml`: db, api, web, Caddy (local HTTPS) |

## Draft epics (to plan)

1. App skeleton and config
2. Database and migrations
3. Provider factories
4. Realtime relay
5. Job queue
6. Events and logging
7. Secrets
8. Recovery and host store
9. API contract and TypeScript client
10. Compose packaging

See `docs/architecture.md`.
