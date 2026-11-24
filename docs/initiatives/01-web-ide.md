**Level:** Initiative · **Status:** Designed

**Purpose:** The browser app where people do everything. Learners pick a project, read the bug report, edit code, use terminals and tasks, run tests, preview the app, chat with the tutor, and submit. Authors create and review issues. The owner manages projects and settings.

**Stack:** Next.js (TypeScript), Monaco, xterm.js, shadcn/ui + Tailwind, TanStack Query (server data) + Zustand (UI state).
**Builds on:** #190 (API, generated TypeScript client, realtime socket), #4 (agent: files, terminals, tasks, ports), #2, #3, #5, #6.
**Layout:** `web/` in the monorepo. See `docs/architecture.md`.

## Key design points

1. **The browser talks only to the backend.** REST through a client generated from OpenAPI, plus one WebSocket for terminals, file events, ports, and toasts. Never to containers directly.
2. **Work is never lost.** Three copies: browser journal (IndexedDB) -> host store on disk (source of truth, #190) -> run volume (#4). Any one can fail.
3. **Laptop only.** No mobile layout. Small screens show a notice.
4. **Syntax now, intelligence later.** Monaco highlighting now; language servers are parked (1.4.6).


## Epic 1.1 — App shell

Layout, themes, shortcuts, and notifications.

| Story | Description | Done when |
|---|---|---|
| 1.1.1 Layout and navigation | Top bar and sidebar: Home, Projects, Runs, Author, Review, Settings. Local mode has no login. Laptop only: below 1024 px the app shows "Open Cerberus on a laptop". | Every page is reachable. |
| 1.1.2 Theme and accessibility | Dark and light themes (Monaco and app colours), keyboard navigation, visible focus, readable contrast. | Both themes pass a contrast check. |
| 1.1.3 Keyboard shortcuts | VS Code style: save, quick open (Ctrl+P), command palette (Ctrl+Shift+P), toggle terminal, run tests. | A shortcut list exists; the main shortcuts work. |
| 1.1.4 Notifications | Toasts and an activity area: port opened, build done, validation result, budget warning. | Backend events show as toasts. |

## Epic 1.2 — Project library

Browse, sync, and inspect projects (#2).

| Story | Description | Done when |
|---|---|---|
| 1.2.1 Project list | Cards: name, languages, tags, latest version, status (available / broken / building), test count. | Synced projects are listed. |
| 1.2.2 Sync and build progress | "Sync" button; build queue with live logs per project; clear errors. | The user can watch a project build. |
| 1.2.3 Project detail | README, versions (commit SHA, date, status), issue count per version, "Free disk space". | Detail page shows version history. |

## Epic 1.3 — Starting and resuming runs

Start, resume, and recover runs (#3, #4).

| Story | Description | Done when |
|---|---|---|
| 1.3.1 New run | Pick project, mode (practice / exam), difficulty range and categories (optional), then Start. | A run starts from the UI. |
| 1.3.2 Startup progress | Live steps: pick or generate issue -> start container -> apply patch -> ready. Cost estimate when generation is needed. | The user sees each step and any error. |
| 1.3.3 Run history and resume | List of runs (project, issue title after submit, status, score, date). Resume reattaches the run volume or restores from the host store (#4.5). | A stopped run resumes where it was left. |
| 1.3.4 Recover interrupted run | After a crash (container, backend, Docker, reboot) the backend marks the run interrupted. The UI shows a banner "This run stopped unexpectedly" and a Recover button; then the browser journal replays. | Kill Docker during a run; after restart, Recover restores every saved edit. |

## Epic 1.4 — Workspace editor

File tree, Monaco tabs, autosave with an offline journal, search, and syntax highlighting.

| Story | Description | Done when |
|---|---|---|
| 1.4.1 File tree | From the agent file API; lock icon on read-only files; create, rename, delete (editable files only); live updates from file-watch events. | The tree matches the container; locked files cannot change. |
| 1.4.2 Editor tabs | Monaco with tabs, split view, dirty markers, read-only mode for locked files. | Edit, save, and split work. |
| 1.4.3 Autosave and offline journal `guided` | Debounced autosave (~1 s) plus Ctrl+S. Unsaved edits queue in IndexedDB (run, file, base hash). Offline badge when the backend is not reachable; replay on reconnect. Base-hash mismatch shows a diff: Keep mine / Keep server. Status: saved / saving / offline / error. | No edit is lost on refresh, network drop, or backend restart. |
| 1.4.4 Search | Quick open (file names) and search across files (agent search). | Ctrl+P and Ctrl+Shift+F work. |
| 1.4.5 Syntax highlighting | Monaco highlighting and bracket matching for Python, TypeScript/JS, HTML, CSS, JSON, YAML, Markdown. | Seed project files highlight correctly. |
| 1.4.6 Language intelligence - parked | Autocomplete and go-to-definition through a language server (pyright, tsserver) in the container, relayed by the agent. | Placeholder. |

## Epic 1.5 — Terminals and tasks

Terminal tabs, task buttons, and per-task output.

| Story | Description | Done when |
|---|---|---|
| 1.5.1 Terminal panel | xterm.js tabs and splits, resize, copy and paste. Gets a terminal token from the backend, then connects to `wss://term-<run>.localhost`; asks for a new token on reconnect after a network drop. | Several terminals work and survive a reload. |
| 1.5.2 Task buttons | Run project and Run tests always visible; other tasks.json tasks in a dropdown; stop and restart. | Buttons call the agent task runner. |
| 1.5.3 Task output | One output tab per running task (e.g. backend, frontend), ANSI colours, clear. | A compound run-project shows one tab per service. |

## Epic 1.6 — Tests panel

Test results from the JUnit report.

| Story | Description | Done when |
|---|---|---|
| 1.6.1 Results tree | Suites -> tests with pass / failure / error, duration, summary counts. | Results show after Run tests. |
| 1.6.2 Failure details | Assertion message and trace; click to jump to the test file and line (read-only). | A failing test opens at the right line. |
| 1.6.3 Re-run and history | Re-run all; pass/fail counts over time in this run (also sent to replay). | History is visible. |

## Epic 1.7 — App preview

Preview running apps inside the IDE.

| Story | Description | Done when |
|---|---|---|
| 1.7.1 Port toasts | "Port 5173 opened - Preview / Open in new tab" when the agent reports a port. | Toast appears within ~2 s of the port opening. |
| 1.7.2 Preview panel | Iframe for `https://<port>-<run>.localhost` with reload, address bar, back/forward; several ports as tabs. | Vite hot reload works in the panel. |
| 1.7.3 Ports list | All open ports with process name; close preview. | The list matches the container. |

## Epic 1.8 — Bug report, session controls, and results

Bug report, timer, submit, result, and replay.

| Story | Description | Done when |
|---|---|---|
| 1.8.1 Bug report panel | Expected / actual / steps / trace for the run issue, pinned at the side. | The report is one click away. |
| 1.8.2 Timer and submit | Timer counts up (practice) or down (exam). Submit asks for confirmation, saves a full snapshot, and starts grading (#6). | Submit starts grading. |
| 1.8.3 Result screen | Score breakdown (#6), test results, files changed, hints used, time, issue origin (#3.6.4) and the original diff, replay link. | All shown after grading. |
| 1.8.4 Replay view | Timeline of events (edits, test runs, hints, tasks) with a scrubber. | A past run can be replayed. |

## Epic 1.9 — Shared chat panel

One chat component for the tutor (#5) and the author assistant (#3).

| Story | Description | Done when |
|---|---|---|
| 1.9.1 Chat component | Streamed messages, Markdown and code blocks, doc citations, tool calls as collapsed steps ("grep 'search' in src/"). | Streams answers from the backend. |
| 1.9.2 Chat modes | Tutor (learner run) and Author assistant (author mode): same component, different endpoint. | Both modes work. |
| 1.9.3 Cost meter | Tokens and estimated cost per message and per session; warning at 80% of budget, stop at 100%. | Cost updates live. |
| 1.9.4 Hint ladder UI | "Give me a hint" button with level 1/2/3; exam mode shows hints left and score cost. | Hint use is recorded. |

## Epic 1.10 — Author mode and review

Create, validate, and review issues in the UI (#3).

| Story | Description | Done when |
|---|---|---|
| 1.10.1 Author workspace | Same workspace as a run, on clean code (authoring session), plus a "Review changes" button. | An author edits and runs tests. |
| 1.10.2 Diff view | Monaco diff editor (inline / side by side) and a changed-files list. | Shows + / - like VS Code. |
| 1.10.3 Issue form | Title, report, category, difficulty, hints; failing tests filled in automatically; Submit, then validation progress. | A draft is submitted and validation shows. |
| 1.10.4 My drafts and validation queue | Drafts with status (validating / failed with reason / in review); queue progress. | The author sees why validation failed. |
| 1.10.5 Review queue | Issues waiting for review with source (UI / MCP / generator); review screen with diff, report, tests, hints, Approve / Edit / Reject (reason required). | An admin approves from the UI. |
| 1.10.6 Needs-update list | Affected issues after a project change: Edit / Regenerate / Retire. | Broken issues can be fixed from the UI. |

## Epic 1.11 — Settings

LLM profiles, budgets, sandbox limits, and MCP setup.

| Story | Description | Done when |
|---|---|---|
| 1.11.1 LLM provider profiles | Add, edit, delete profiles (provider, base URL, model, key); Test connection; the key is never shown again after save (#190 secrets). | A profile works for the tutor. |
| 1.11.2 Model routing and budgets | Model for text and model for code; budget per session and per month; pool pre-fill switch with cost estimate. | Settings are used by #5 and #3. |
| 1.11.3 Sandbox settings | CPU, RAM, disk limits, idle timeout, Docker status check. | Changes apply to new sessions. |
| 1.11.4 MCP setup page | HTTPS URL, token, local CA download and trust steps, config snippets for Claude Code, Codex, Cursor. | An author connects with this page only. |

## Epic 1.12 — Hosted mode UI (parked)

Placeholders for hosted mode (#7).

| Story | Description | Done when |
|---|---|---|
| 1.12.1 Login and orgs - parked | OIDC or email login, org switcher, roles shown. | Placeholder. |
| 1.12.2 Admin and exams - parked | Groups, exam creation and assignment, result dashboards. | Placeholder. |

## Order

```
1.1.1 -> 1.4.1-1.4.3 -> 1.5.1-1.5.2 -> 1.6.1-1.6.2   (first usable workspace)
-> 1.3.1-1.3.2 -> 1.8.1-1.8.2 -> 1.7 -> 1.5.3 -> 1.4.4-1.4.5
-> 1.11.1 -> 1.9.1-1.9.2 -> 1.9.3-1.9.4 -> 1.8.3 -> 1.2 -> 1.3.3-1.3.4
-> 1.10 -> 1.11.2-1.11.4 -> 1.8.4 -> 1.1.2-1.1.4
```

**First milestone:** open a `flask-notes` run -> file tree with locks -> edit with autosave -> terminal -> Run tests shows failures -> fix the bug -> tests pass.

## Decisions

- Backend is a separate initiative (#190). #1 is UI only.
- Autosave by default (debounced ~1 s) plus Ctrl+S; offline journal in IndexedDB; conflicts show a diff, never a silent overwrite.
- Laptop only (>= 1024 px).
- Syntax highlighting now; language intelligence parked.
- shadcn/ui + Tailwind; TanStack Query + Zustand.

## Log events (sent to the backend)

`run.start`, `run.edit`, `run.test`, `run.hint`, `run.submit`, `run.recover`, `workspace.journal.replay`, `workspace.conflict`
