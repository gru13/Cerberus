# Cerberus

A debugging practice and exam platform.

The user opens a web IDE (like VS Code). The IDE loads a correct base project with one injected bug. The user finds and fixes the bug. Tests check the fix: the project tests (visible, read-only) and optional held-out grading tests. An AI tutor helps with questions and documentation, but it does not give the fix.

## Status

Design phase. All 8 initiatives are designed (see `docs/initiatives/`). No application code yet.

## Key decisions

- First language: **Python**. Frontend: **Next.js + Monaco**. Backend: **FastAPI**. Sandbox agent: **Rust**.
- Local install: **`docker compose up`**.
- Accounts: **per user**.
- LLM: **user brings their own API key**. The user pays for LLM use.
- Projects: each base project is correct and versioned.
- Issues: each issue is a versioned diff, stored in a database, applied to a base project version.
- A run uses an issue from the pool or a newly generated issue (hybrid). Each new issue is validated: tests fail before the fix and pass after it.
- Tutor: Socratic questions, function and class explanations from the docs, generic samples. Never the fix.
- Modes: practice and exam.

## Repository layout

| Path | Contents |
|------|----------|
| `CLAUDE.md` | Rules for AI coding sessions (logging in ASD-STE100) |
| `docs/` | Design notes, decisions, ontology |
| `docs/decisions/` | One file per agreed design decision |
| `docs/ontology.md` | Entity types and verbs for logs and the knowledge graph |
| `logs/` | Structured JSON-lines logs (issue lifecycle, runs) |
| `docs/architecture.md` | Planned layout: `web/` (Next.js), `api/` (FastAPI), `agent/` (Rust), `protocol/` |
| `docs/initiatives/` | Initiative designs (1–8; initiative 8 is issue #190) |

## Logging

All logs use ASD-STE100 Simplified Technical English and JSON lines with subject–predicate–object triples. See `CLAUDE.md`.
