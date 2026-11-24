**Level:** Initiative · **Status:** Designed

**Purpose:** Run the learner's dev box safely. Start a container from the project image, apply the issue patch, remove every trace, lock read-only files, and give the IDE terminals, files, tasks, and app previews. Also run the throwaway test runs for validation (#3) and grading (#6).

**Builds on:** #2 (project image, `workdir`, `run-project` / `run-tests`, editable and read-only patterns), #3 (run package), decision 0001 (`SandboxExecutor`: LocalDocker now, WorkerPool later).
**Used by:** #1 (IDE), #3 (authoring sessions, validation), #5 (tutor tools), #6 (grading, replay events).

**Guided work:** the in-container agent (Epic 4.3) is written in **Rust by the owner**. Claude acts as guide: explains, reviews, and suggests; it does not write the agent code unless asked. These stories have the `guided` label.

## Key design points

1. **Agent in every container.** A small static Rust binary copied in at start. No change to project Dockerfiles. It owns terminals, files (with lock rules), tasks, port detection, tutor tools, and the event stream. The backend talks to it over a mounted Unix socket.
2. **No internet, but previews work.** Each dev box joins its own Docker `--internal` network: the backend can reach it; it cannot reach the internet. Throwaway runs use `--network none`.
3. **Real read-only files.** Editable files belong to `runner`; others are root-owned `444`; directories have the sticky bit. The agent API also rejects writes. Grading from a clean copy is the final guard.
4. **Trace removal.** Patch applied as root in the running container (not in an image layer). Then delete `.orig` / `.rej` / patch, set one fixed mtime, clear caches and shell history, and assert no `.git`.
5. **Work survives crashes.** The workspace lives on a named volume per run, so a new container reattaches it. The backend host store (#190) holds a write-through copy of learner files and is the source of truth.


## Epic 4.1 — SandboxExecutor and container lifecycle

Start, harden, track, and clean up dev box containers.

| Story | Description | Done when |
|---|---|---|
| 4.1.1 SandboxExecutor interface | `create(run_package) -> session`, `exec`, `stop`, `snapshot`, `destroy`. `LocalDocker` now; `WorkerPool` parked. | Interface and LocalDocker work. |
| 4.1.2 Container hardening `guided` | Non-root user, `--cap-drop ALL`, `no-new-privileges`, default seccomp, read-only root FS, workspace on a named volume per run (`cerberus-run-<id>`), tmpfs `/tmp`, limits: PIDs, 2 CPU, 4 GB RAM, 5 GB disk (configurable). | Hardening checklist passes. |
| 4.1.3 Session lifecycle | starting -> patching -> ready -> idle -> stopped -> destroyed. Idle timeout 30 min (snapshot then stop). One active session per user in local mode. | States are logged (`sandbox.session.*`). |
| 4.1.4 Startup and health checks | Docker present and running; image present (or built by #2); clear errors. Startup target < 5 s. | Clear message when Docker is missing. |
| 4.1.5 Sandbox cleanup | Destroy stopped sessions. Remove a run volume when the run is submitted or deleted. Remove orphan containers, networks, and volumes on app start. | No leftovers after a crash. |

## Epic 4.2 — Workspace preparation

Apply the patch, remove all traces, and lock read-only files.

| Story | Description | Done when |
|---|---|---|
| 4.2.1 Apply patches | Apply run-package patches as root, in order. Fail the session with a clear error on reject. | Patched workspace ready. |
| 4.2.2 Trace removal `guided` | Delete `.orig` / `.rej` / patch files; remove `grading_tests` paths (#6.1.2); set one fixed mtime on all files; clear `__pycache__`, `*.pyc`, `.vite`, `.cache`, shell history; assert no `.git`. | Trace test finds nothing (`ls -lt`, `find -newer`, `.pyc`). |
| 4.2.3 Read-only locks `guided` | Editable files owned by `runner`; others root-owned `444`; sticky bit on directories; matched against editable and read-only patterns. Learners may create new files (ignored by grading). | Learner cannot edit, delete, or rename a locked file. |
| 4.2.4 Authoring workspace | Authoring sessions (#3): no patch, clean copy outside the workspace (`/opt/cerberus/clean`, agent-only) for diffs. | Diff API works in authoring mode. |

## Epic 4.3 — In-container agent (Rust)

A small static Rust binary copied into each container. The owner builds it; Claude guides.

| Story | Description | Done when |
|---|---|---|
| 4.3.1 Agent skeleton and transport `guided` | Rust static binary (musl) for x86_64 and aarch64. Copied in at start. Listens on a mounted Unix socket. Versioned protocol (JSON or MessagePack). Suggested crates: `tokio`, `serde`, `clap`, `tracing`. | Backend to agent ping works on amd64 and arm64. |
| 4.3.2 Agent file API `guided` | list / read / write / rename / create / delete / search with lock rules; file-watch events. Suggested crates: `notify`, `ignore`/`globset`. | IDE file tree and edits work through the agent. |
| 4.3.3 Agent terminal API `guided` | Many PTYs (bash, else sh), resize, streamed through the backend over WebSocket. Suggested crate: `portable-pty`. | Several terminal tabs work. |
| 4.3.4 Agent task runner `guided` | Parse `tasks.json`; run `run-project` (with `dependsOn`, parallel/sequence, background) and `run-tests`, plus optional tasks; stream output per task; stop and restart. | IDE buttons run tasks. |
| 4.3.5 Agent port detection `guided` | Poll `/proc/net/tcp` and `tcp6` (~1 s) for new LISTEN ports; emit `port.open` / `port.close`. Suggested crate: `procfs`. | "Port 5173 opened" reaches the IDE. |
| 4.3.6 Agent tutor tools `guided` | Allow-listed read-only commands for the tutor (#5): `ls`, `cat` with line range, `grep`/`rg`, `find`, `python -c help()`. Timeout and output size limit. No writes. | Tutor can grep the learner code safely. |
| 4.3.7 Agent event stream `guided` | Edit (file + diff hash), test run (results), task start/stop, terminal command (command only), port events. Sent to the backend for replay (#6) and logs (STE100). | Events are stored per run. |

## Epic 4.4 — Network and preview

No internet in the dev box, but app previews still work.

| Story | Description | Done when |
|---|---|---|
| 4.4.1 Internal network per session `guided` | Docker `--internal` network: backend can reach the container; the container cannot reach the internet. | `curl` to the internet fails inside; preview works. |
| 4.4.2 Preview proxy `guided` | HTTPS reverse proxy backend -> container:port, WebSocket support (hot reload), session-token check. | A Vite app with hot reload works in preview. |
| 4.4.3 Preview URLs | Subdomain per port: `https://<port>-<run>.localhost` (no DNS setup; avoids path-prefix breakage). | Several ports preview side by side. |
| 4.4.4 No network for throwaway runs `guided` | Validation and grading runs use `--network none`. | No network in validation or grading. |

## Epic 4.5 — Persistence and resume

Save and restore the learner workspace.

| Story | Description | Done when |
|---|---|---|
| 4.5.1 Host store and snapshots `guided` | The backend keeps a write-through copy of every editable and new file in the host store (`~/.cerberus/runs/<run>/files/`, content-addressed). Editor saves are copied on write; terminal changes arrive through agent file-watch events. Full snapshot on submit. | After the run volume is deleted, no saved edit is lost. |
| 4.5.2 Resume a session `guided` | Fast path: new container on the same run volume. Slow path (volume lost): fresh container -> apply patch -> remove traces -> restore from the host store -> lock again. | Both paths work; the learner continues where they stopped. |
| 4.5.3 SnapshotStore interface | Uses the #190 store interface: local folder (local mode) or object storage (hosted). | Same code in both modes. |

## Epic 4.6 — Throwaway test runs

Clean-copy test execution for the #3 validator and #6 grading.

| Story | Description | Done when |
|---|---|---|
| 4.6.1 Clean-copy runner `guided` | Fresh container, `--network none` -> apply patches -> copy in only allowed editable files from the host store -> keep `grading_tests` (#6.1.2) -> `run-tests` -> collect JUnit -> destroy. | Returns JUnit report, exit code, runtime. |
| 4.6.2 Test run modes `guided` | `baseline` (no patch), `patched`, `reversed`, `learner` (patch + learner edits). | All four modes work. |
| 4.6.3 Test run limits and queue `guided` | One at a time locally; timeout (`run-tests` <= 120 s + overhead). | Queue and timeout are enforced. |

## Epic 4.7 — Hosted executor (parked)

Placeholders for hosted mode.

| Story | Description | Done when |
|---|---|---|
| 4.7.1 WorkerPool executor - parked | Remote workers, scheduling, per-user quotas, pull by digest. | Placeholder. |
| 4.7.2 Stronger isolation - parked | gVisor (`runsc`) or Kata containers for untrusted users. | Placeholder. |

## Order

```
4.1.1-4.1.4 -> 4.2.1-4.2.3 -> 4.3.1-4.3.4 -> 4.6.1-4.6.2 (unblocks #3 validator)
-> 4.4.1-4.4.3 + 4.3.5 (preview) -> 4.3.6-4.3.7 -> 4.2.4 (authoring) -> 4.5 -> 4.1.5 -> 4.6.3
```

**First milestone:** start `flask-notes` with one patch -> trace test passes -> terminal works -> `run-tests` shows failing tests -> `run-project` -> preview opens.

## Decisions

- Docker first (Docker Desktop on Mac/Windows, Docker Engine on Linux). Podman later.
- Agent in Rust, built by the owner with Claude as guide (`guided` label).
- Preview URL: `https://<port>-<run>.localhost`.
- Default limits: 2 CPU, 4 GB RAM, 5 GB disk (configurable). Idle timeout 30 min.
- Learners can create new files; grading ignores them.
- Workspace on a named volume per run; the host store is the source of truth for learner work.
- Local mode trusts the user; exam integrity checks belong to hosted mode (#7).
- WorkerPool and stronger isolation are parked.

## Log events

`sandbox.session.start|ready|idle|stop|destroy`, `sandbox.patch.apply|fail`, `sandbox.trace.clean`, `sandbox.task.start|stop`, `sandbox.port.open|close`, `sandbox.snapshot.save|restore`, `sandbox.testrun.start|end`
