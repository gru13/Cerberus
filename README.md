# Cerberus

A debugging practice and exam platform.

The user opens a web IDE (like VS Code). The IDE loads a correct base project with one injected bug. The user finds and fixes the bug. Tests check the fix: the project tests (visible, read-only) and optional held-out grading tests. An AI tutor helps with questions and documentation, but it does not give the fix.

**Start here: [design index](docs/README.md)**: all initiatives, architecture, decisions, and the proposed build order.

## Status

Design phase is complete: 8 initiatives, 65 epics, 283 stories on the [workboard](https://github.com/users/gru13/projects/4). No application code yet.

## Key decisions

- **Stack:** Next.js + Monaco + xterm.js (web), FastAPI on Python 3.13 (api), Rust (in-container agent, built by the owner), Postgres only (data, job queue, events). No Kafka or Redis.
- **Install:** `docker compose up` (local mode). Hosted mode for colleges and companies is designed and parked ([decision 0001](docs/decisions/0001-deployment-modes.md)).
- **Projects:** any stack. Each project gives a Dockerfile and `tasks.json` with `run-project` and `run-tests`. A merge to `cerberus-content` builds a new version (commit SHA).
- **Issues:** a versioned diff on one project version. Created in the UI or through MCP, validated (tests fail before the fix, pass after), and reviewed before use.
- **Dev box:** Docker container per run. Patch applied, traces removed, read-only files locked, no internet, app previews at `https://<port>-<run>.localhost`.
- **Work is never lost:** browser journal, host store (source of truth), and run volume.
- **Grading:** clean copy, optional held-out tests. Score: correctness 60, time 15, hints 15, change size 10.
- **Tutor:** the user's own LLM key (OpenAI-compatible or Anthropic). Socratic, docs-based, server-side guardrails. Never the fix. Hints work without a key.
- **Modes:** practice and exam (self-exam locally; assigned exams in hosted mode).

## Repository layout

| Path | Contents |
|------|----------|
| `CLAUDE.md` | Rules for AI coding sessions: STE100 logging, build log, git safety, guided work |
| `docs/README.md` | Design index (start here) |
| `docs/architecture.md` | Planned layout: `web/`, `api/`, `agent/`, `protocol/`; persistence |
| `docs/initiatives/` | One design doc per initiative (1–8; initiative 8 is issue #190) |
| `docs/decisions/` | Long-form design decisions |
| `docs/ontology.md` | Entity types and verbs for logs and the knowledge graph |
| `logs/build.jsonl` | Build log: decisions, status changes, failures |
| `.githooks/`, `.github/` | Commit and push hooks, linked-issue check, PR template, CODEOWNERS |

## Contributing

Only the owner merges. Every change goes through a pull request that closes an open issue (`Closes #n`). See `CLAUDE.md` for the rules.

## Logging

All logs use ASD-STE100 Simplified Technical English and JSON lines with subject–predicate–object triples. See `CLAUDE.md`.
