# Cerberus design index

The master index for the Cerberus design. Start here.

- **Status:** design phase is complete. All 8 initiatives are designed. No application code yet.
- **Board:** [Cerberus Workboard](https://github.com/users/gru13/projects/4). Views: **My work** (what needs the owner), **Roadmap** (open work by initiative and phase), **Done**. Status: Designing → Backlog → Ready → In progress → In review → Done, plus Parked. Fields: Initiative, Phase, Built by, Claude %.
- **Rules for contributors and AI sessions:** [`CLAUDE.md`](../CLAUDE.md) (logging in ASD-STE100, build log, git safety, guided work)

## What Cerberus is

A debugging practice and exam platform. A web IDE opens a correct base project with one injected bug (an issue diff). The learner finds and fixes the bug. Tests grade the fix from a clean copy. A guardrailed AI tutor (the learner's own API key) asks Socratic questions and explains docs, but never gives the fix.

## Core documents

| Document | Contents |
|---|---|
| [`architecture.md`](architecture.md) | Request path, monorepo layout (`web/`, `api/`, `agent/`, `protocol/`), runtime data, work persistence and failure matrix |
| [`decisions/0001-deployment-modes.md`](decisions/0001-deployment-modes.md) | Local and hosted modes, tenancy, roles, provider interfaces |
| [`ontology.md`](ontology.md) | Entity types and verbs for logs and the knowledge graph |
| [`../logs/build.jsonl`](../logs/build.jsonl) | Build log: decisions, status changes, failures (JSON lines) |

## Initiatives

| # | Initiative | Issue | Epics | Stories (parked) | Design doc |
|---|---|---|---|---|---|
| 0 | Project management | #377 | 2 | repo setup, design records | [00-project-management.md](initiatives/00-project-management.md) |
| 1 | Web IDE | #1 | 12 | 46 (3) | [01-web-ide.md](initiatives/01-web-ide.md) |
| 2 | Project repository | #2 | 4 | 20 (1) | [02-project-repository.md](initiatives/02-project-repository.md) |
| 3 | Issue engine | #3 | 10 | 47 (1) | [03-issue-engine.md](initiatives/03-issue-engine.md) |
| 4 | Sandbox runner | #4 | 7 | 28 (2) | [04-sandbox-runner.md](initiatives/04-sandbox-runner.md) |
| 5 | AI tutor | #5 | 8 | 40 (2) | [05-ai-tutor.md](initiatives/05-ai-tutor.md) |
| 6 | Scoring and grading | #6 | 6 | 25 (2) | [06-scoring-grading.md](initiatives/06-scoring-grading.md) |
| 7 | Users and accounts | #7 | 6 | 23 (15) | [07-users-accounts.md](initiatives/07-users-accounts.md) |
| 8 | Platform backend | #190 | 12 | 54 (2) | [08-platform-backend.md](initiatives/08-platform-backend.md) |
| | **Total** | | **65** | **283 (28)** | |

Initiative 8 is issue #190 because issue #8 was already used. Docs call it "initiative 8 (#190)".

### One line per initiative

1. **Web IDE** — Next.js + Monaco + xterm.js. Workspace, terminals, tests panel, preview, chat panel, author and review screens. Laptop only.
2. **Project repository** — `cerberus-content` monorepo. Each project has a Dockerfile, `tasks.json` (`run-project`, `run-tests`), and `project.yaml`. Merge → build → register by commit SHA.
3. **Issue engine** — An issue is a diff + project version. Authored in the UI or through MCP, validated (fail before, pass after), reviewed, versioned, exported as JSONL.
4. **Sandbox runner** — Docker dev box per run: patch applied, traces removed, read-only locks, no internet, port previews. Rust in-container agent (owner builds it, `guided`).
5. **AI tutor** — Shared LLM layer (adapters, budgets). Socratic tutor with server-side guardrails. Guardrails get a deep design session first (5.5.7).
6. **Scoring and grading** — Clean-copy grading with optional held-out tests. Formula v1: correctness 60, time 15, hints 15, change size 10. Replay and stats.
7. **Users and accounts** — Local profile, provider profiles, MCP tokens, data export, one exam model. Hosted identity and orgs are parked.
8. **Platform backend** — FastAPI modular monolith, Postgres only (data, queue, EventBus), realtime relay, STE100 logging, host store, run orchestration, compose packaging.

## How the parts connect

```
Browser (#1) ──REST + WebSocket──► API (#190) ──► Postgres (data, queue, events)
                                      │
             ┌────────────┬───────────┼─────────────┬──────────────┐
             ▼            ▼           ▼             ▼              ▼
        Projects (#2)  Issues (#3)  Sandbox (#4)  Tutor + LLM (#5)  Scoring (#6)
                                      │
                                      ▼
                             Rust agent in dev box
Accounts, exams, tokens (#7) and run orchestration (#190) tie a run together.
```

## Ownership

The owner builds the `guided` stories to learn (security, performance, core systems; about 40% of the effort). Claude explains and reviews these, and builds everything else (about 60%: UI, app skeleton, CRUD, compose and CI). On the board, `guided` stories are assigned to the owner. Study guide for these stories: [guided-study-guide.md](guided-study-guide.md); official sources: [learn/](learn/README.md).

| Area | Owner stories (`guided`) |
|---|---|
| Sandbox and Rust agent | 4.3.1–4.3.7 agent · 4.1.2 hardening · 4.2.2 trace removal · 4.2.3 read-only locks · 4.4.1, 4.4.2, 4.4.4 network and preview proxy · 4.5.1–4.5.2 snapshots and resume · 4.6.1–4.6.3 clean-copy runner · 8.9.3 agent protocol · 8.10.4 agent binary builds |
| Realtime and persistence | 8.4.1–8.4.4 realtime relay · 8.8.1–8.8.5 host store and recovery · 1.4.3 offline journal · 8.5.2 job leases |
| AI safety and retrieval | 5.5.1–5.5.7 guardrails · 5.3.5 untrusted tool output · 5.3.3 symbol docs tool · 3.4.10 MCP safety |
| Data integrity and generation | 3.5.2 validator test checks · 3.8.1–3.8.4 carry-over · 3.7.1–3.7.4 LLM bug generator · 3.10.1 issue picking · 6.1.2–6.1.4 held-out tests, pass rules, flake guard |
| Platform security | 8.1.5 local security · 8.2.2 tenancy guard · 8.7.1, 8.7.2, 8.7.4 secrets and tokens · 8.10.2 Docker socket proxy · 2.2.3 Dockerfile rules |

Total: 61 stories and 7 epics (4.3, 5.5, 8.4, 8.8, 3.8, 3.7, 4.6). Claude builds 8.9.5, a fake agent for tests, so backend and UI work does not wait for the Rust agent.

## Build order

Each story has a `Phase` field on the board with these values. Stories in the current phase are `Ready`.

| Phase | Goal | Main stories |
|---|---|---|
| 0 Foundations | `docker compose up` shows a health page | #190 8.1–8.3, 8.6.1, 8.10.1, 8.10.3 · #2 2.1, 2.2 |
| 1 Dev box | A patched `flask-notes` container with a working terminal | #2 2.4.2, 2.3.1–2.3.3 · #4 4.1–4.3 (agent, `guided`), 4.6 · #190 8.4, 8.5, 8.8.1–8.8.3 |
| 2 Workspace | First #1 milestone: edit, run tests, see failures, fix, pass | #1 1.1.1, 1.4.1–1.4.3, 1.5.1–1.5.2, 1.6.1–1.6.2 · #190 8.9.1–8.9.2 |
| 3 Runs and grading | Start a run, submit, see a score | #190 8.11 · #3 3.1, 3.4 (validator), 3.10.1 · #6 6.1.1, 6.1.3, 6.2.1, 6.3 |
| 4 Authoring | Create, validate, and review an issue in the UI and through MCP | #3 3.2, 3.3, 3.6 · #1 1.10 |
| 5 Tutor | Socratic tutor with guardrails | #5 5.5.7 (deep design) first, then 5.1–5.3, 5.5–5.6 · #1 1.9 |
| 6 Complete local | Preview, replay, stats, self-exams, settings, remaining stories | #4 4.4–4.5 · #6 6.4–6.6 · #7 7.1, 7.2.1–7.2.3, 7.6.1 · #1 rest |
| Later | Hosted mode | All parked stories |

## Decision log

Generated from `logs/build.jsonl`. Newer decisions win.

| Date | Decision | Summary | Note |
|---|---|---|---|
| 2026-11-16 | `stack` | The user selects Next.js, Monaco, and Docker for the platform. |  |
| 2026-11-16 | `issue-model` | The user selects a correct base project and versioned issue diffs in a database. |  |
| 2026-11-16 | `tutor-policy` | The tutor asks questions and explains documentation. The tutor does not give the fix. |  |
| 2026-11-16 | `first-scope` | The first scope is Python projects and a basic frontend. | Refined: seed projects are Python, Node, and full stack (#2) |
| 2026-11-16 | `byo-api-key` | Each user gives an own LLM API key. The user pays for LLM use. |  |
| 2026-11-16 | `hidden-tests` | The user sees the code only. Hidden tests run in a separate grading container. | Superseded by `project-contract` and `grading-tests` |
| 2026-11-16 | `image-layers` | The image store has base and project images. The sandbox applies issue patches at run start. | Superseded by `project-contract` (no shared base image) and `auto-versioning` |
| 2026-11-16 | `llm-adapter` | The tutor uses a provider adapter. It supports OpenAI-compatible APIs and Anthropic. | Detailed in #5 Epic 5.1 |
| 2026-11-16 | `tutor-rag` | The tutor uses project docs and pinned library docs. The model does not see the fix. | Refined by `tutor-docs` |
| 2026-11-16 | `app-preview` | The user runs the app server in the sandbox and sees it in a preview panel. |  |
| 2026-11-16 | `repo-safety` | Main accepts changes only through a PR. Each PR links an open issue. Only the owner has write access. |  |
| 2026-11-18 | `project-contract` | Each project gives a Dockerfile and tasks.json with run-project and run-tests. Tests are visible and read-only. |  |
| 2026-11-18 | `issue-as-diff` | An issue is a diff and a project version. The dev box has no git. |  |
| 2026-11-18 | `auto-versioning` | A merge starts a build. The commit SHA identifies the version. The registry is parked. |  |
| 2026-11-18 | `0001-deployment-modes` | Cerberus has local and hosted modes. The first release builds local mode only. |  |
| 2026-11-18 | `issue-authoring` | Authors create issues in the UI or through MCP. There is no CLI. MCP uses HTTPS only. |  |
| 2026-11-18 | `issue-review` | Each issue gets a review before it is active. MCP cannot approve an issue. |  |
| 2026-11-18 | `issue-dataset` | The database keeps the issues. Public issues go to GitHub as JSONL through a data pull request. |  |
| 2026-11-22 | `sandbox-agent-rust` | The in-container agent uses Rust. The owner writes it. Claude guides and reviews. |  |
| 2026-11-22 | `sandbox-network` | The dev box uses an internal network without internet. Test runs use no network. |  |
| 2026-11-22 | `sandbox-defaults` | Docker comes first. Previews use port subdomains on localhost. Limits are 2 CPU, 4 GB RAM, and 5 GB disk. |  |
| 2026-11-22 | `platform-backend` | Initiative 8 owns the shared backend. Each initiative owns its own endpoints and tables. |  |
| 2026-11-22 | `backend-python` | The backend uses Python and FastAPI. It is one modular package. |  |
| 2026-11-22 | `work-persistence` | Learner work has three copies: browser journal, host store, and run volume. The host store is the source of truth. |  |
| 2026-11-22 | `web-stack` | The web app uses shadcn/ui, Tailwind, TanStack Query, and Zustand. It supports laptops only. |  |
| 2026-11-22 | `repo-layout` | One monorepo holds web, api, and agent. A JSON Schema defines the agent protocol. Caddy gives local HTTPS. |  |
| 2026-11-22 | `run-orchestration` | Initiative 8 owns the run state machine. Each run step stays with its owner. |  |
| 2026-11-22 | `no-broker` | Postgres holds the data, the job queue, and the event bus. Cerberus uses no Kafka. |  |
| 2026-11-22 | `backend-runtime` | A separate worker runs jobs with procrastinate. Docker access goes through a socket proxy. |  |
| 2026-11-22 | `backend-tooling` | The backend uses Python 3.14 (was 3.13 until 2026-11-25), uv, ruff, and ty. Release images go to GHCR. |  |
| 2026-11-22 | `0001-deployment-modes` | Decision 0001 adds the BlobStore and EventBus interfaces. |  |
| 2026-11-22 | `preview-contract` | Project servers bind to 0.0.0.0. Frontends call backends by a relative path through the dev-server proxy. |  |
| 2026-11-22 | `tutor-exam-mode` | Exam mode keeps code and tools. Server checks block fix code, rewritten project code, and direct answers. |  |
| 2026-11-22 | `tutor-guardrail-design` | Tutor guardrails get a deep design session before any guardrail code. |  |
| 2026-11-22 | `tutor-no-key` | Without an LLM key, the hint button shows the author hints. |  |
| 2026-11-22 | `tutor-docs` | The tutor reads library docs in the dev box. Doc packs use full-text search. Embeddings are parked. |  |
| 2026-11-22 | `llm-layer` | Initiative 5 owns the shared LLM layer. The issue engine uses it. Chats stay in the local database. |  |
| 2026-11-22 | `grading-tests` | Projects can declare held-out grading tests. The dev box does not have them. |  |
| 2026-11-22 | `score-formula-v1` | The score has correctness 60, time 15, hints 15, and change size 10. Test runs cost nothing. |  |
| 2026-11-22 | `score-rules` | Idle time does not count. Alternative fixes get the same score. The hardcode check only flags. |  |
| 2026-11-22 | `single-issue-runs` | Each run has one issue in version 1. Practice scores count less in the skill profile. |  |
| 2026-11-22 | `exam-model` | Local self-exams and hosted exams use one exam model. The server timer submits at the end. |  |
| 2026-11-22 | `hosted-login` | Hosted login uses OIDC or an email link. Cerberus stores no passwords. |  |
| 2026-11-22 | `hosted-exam-rules` | Hosted exams pick from equal-difficulty issues. The diff shows after the exam window closes. |  |
| 2026-11-22 | `accounts-scope` | Local mode has one user. Cerberus has no leaderboards by default. Self-exams count as exams. |  |

## Repositories

| Repository | Visibility | Contents |
|---|---|---|
| `gru13/Cerberus` | private (open source later) | Platform: design docs, `web/`, `api/`, `agent/` |
| `cerberus-content` | private (planned) | Projects: one folder per project |
| `cerberus-issues` | public (planned) | Public issue dataset as JSONL (CC BY 4.0) |
