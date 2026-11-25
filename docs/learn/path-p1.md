# Phase 1 study path

A reading and practice order for the Phase 1 guided stories. Nine modules, from basics to the stories.

- **Concepts:** each id is in `docs/learn/concepts/<area>.yaml`. Read the notes and the primary source there. Run `uv run docs/learn/learn.py edit` to browse them.
- **Stories:** story details (Goal, Pitfalls, Test) are in `docs/guided-study-guide.md`. Read the story entry after its module, not before.
- **Order:** the modules follow the build order in section (a) of the study guide. Do them in sequence. Each module lists what it needs.
- **Exercises:** each exercise is a throwaway script. Keep it outside the repo, for example in `~/scratch/`. It is practice, not story code.
- **Python:** use 3.14. **Rust:** use stable, with `cargo` and `clippy`.

## Scope

- **In:** the 22 stories marked P1 in the study guide, plus 5 stories marked P6 "needed in P1" (the guide pulls them forward): 8.9.3, 8.10.4, 4.4.1, 4.4.2 (terminal route only) and 8.7.4 (terminal token only). They are marked **pulled** below.
- **Out:** all P0 stories (8.1.5, 8.2.2, 8.10.2, 2.2.3) and all later phases. Their concepts appear only as read-ahead where a P1 story uses them.
- **Out (preview part of 4.4.2, P6):** `sandbox.caddy-admin-api`, `sandbox.csp-frame-ancestors`, `sandbox.iframe-sandbox`.

## Module map

| # | Module | Stories |
|---|---|---|
| 1 | Wire contract and framing | 8.9.3 (pulled), 4.3.1 (framing part) |
| 2 | Rust agent core | 4.3.1, 8.10.4 (pulled) |
| 3 | Container hardening | 4.1.2 |
| 4 | Files, permissions and traces | 4.2.2, 4.2.3, 4.3.2 |
| 5 | Agent link and durable store | 8.4.2, 8.8.1, 8.8.3, 8.8.2 |
| 6 | Events and the browser socket | 8.4.4, 8.4.1, 4.3.7 |
| 7 | The terminal path | 8.7.4 (pulled), 4.4.1 (pulled), 4.4.2 (pulled), 4.3.3, 8.4.3 |
| 8 | Agent tasks, ports and tutor tools | 4.3.4, 4.3.5, 4.3.6 |
| 9 | Test runs and job leases | 8.5.2, 4.6.1, 4.6.2, 4.6.3 |

---

## Module 1: Wire contract and framing

- **Needs:** basic Python typing and Pydantic. A first read of Rust enums and `serde`. No other module.
- **Why first:** the schema is the contract that the Rust agent, the Python client and the fake agent (8.9.5) share.
- **Read:**
  1. `protocol.json-schema-2020-12`
  2. `protocol.pydantic-discriminated-unions`
  3. `protocol.serde-tagged-enums`
  4. `protocol.datamodel-code-generator`
  5. `protocol.jsonschema-crate`
  6. `protocol.schemars` (optional, for comparing)
  7. `protocol.base64-rfc4648`
  8. `protocol.json-number-precision`
  9. `protocol.protocol-semver`
  10. `protocol.ndjson-framing`
  11. `protocol.messagepack` (decide JSON or MessagePack; see the pitfall in 4.3.1)
  12. `sandbox.length-delimited-codec`
- **Exercise:** model two messages (`ping` and `write_file` with a base64 body) with a `type` tag.
  - Write the JSON Schema by hand.
  - Generate Pydantic models from it.
  - Write the matching Rust `serde` enum.
  - Validate one fixture on both sides. Then break the fixture and check that both sides fail.
- **Done when:** you can say why `oneOf` + `const` maps to both a Pydantic discriminated union and a serde tagged enum.
- **Prepares:** **8.9.3** #242 (pulled). **4.3.1** #107 (framing and format choice only).

## Module 2: Rust agent core

- **Needs:** Module 1. Rust basics: ownership, `Result`, traits, `async`/`await`.
- **Read:**
  1. `sandbox.thiserror`
  2. `sandbox.tracing-json`
  3. `sandbox.tokio-unixlistener`
  4. `sandbox.tokio-select-cancel`
  5. `sandbox.unix-socket-peercred`
  6. `sandbox.pid1-zombie-reaping`
  7. `sandbox.rustix`
  8. `build.rust-musl-targets`
  9. `build.cargo-release-profile`
  10. `build.cross-rs` and `build.cargo-zigbuild` (choose one)
  11. `build.mimalloc`
  12. `build.reproducible-builds`
  13. `security.docker-image-inspect` (P0 read-ahead: pick the binary by image architecture)
- **Exercise:** write a Unix-socket server with `tokio` that answers `ping` with `pong` using length-delimited frames.
  - Stop it cleanly on SIGTERM with a cancellation token.
  - Print the peer uid from `SO_PEERCRED`.
  - Build it for a musl target. Run `file` on the binary and run it in an `alpine` container.
- **Done when:** the binary is static, and a `kill -9` followed by a restart rebinds the socket.
- **Prepares:** **4.3.1** #107, **8.10.4** #248 (pulled, local musl build only).

## Module 3: Container hardening

- **Needs:** Docker basics. Module 2 for the agent that runs inside the box.
- **Read:**
  1. `sandbox.docker-run-hardening-flags`
  2. `sandbox.capabilities`
  3. `sandbox.proc-status-fields`
  4. `sandbox.seccomp`
  5. `sandbox.cgroup-v2-limits`
  6. `sandbox.docker-volume-copyup`
  7. `sandbox.userns-rootless`
  8. `sandbox.docker-sdk-engine`
- **Exercise:** run a container with the full flag set from 4.1.2.
  - Read `CapEff`, `NoNewPrivs` and `Seccomp` from `/proc/self/status` inside it.
  - Run a fork bomb with a PID limit. Check that the host stays fine.
  - Show that a named volume copies the image files only when it is empty.
  - Show which prep step fails without `CAP_CHOWN`. This is the prep-container question in the guide.
- **Done when:** you can explain why the prep container needs capabilities that the dev box must not have.
- **Prepares:** **4.1.2** #97.

## Module 4: Files, permissions and traces

- **Needs:** Modules 2 and 3. Linux file basics: owner, mode, inode.
- **Read:**
  1. `sandbox.inode-timestamps`
  2. `sandbox.utimensat`
  3. `sandbox.gnu-patch-reverse`
  4. `sandbox.pyc-files`
  5. `sandbox.sticky-bit-permissions`
  6. `sandbox.protected-links-sysctl`
  7. `sandbox.python-pathspec`
  8. `sandbox.globset`
  9. `sandbox.rename-atomic`
  10. `sandbox.openat2`
  11. `sandbox.inotify`
  12. `sandbox.notify-crate`
  13. `sandbox.grep-searcher`
- **Exercise:** in a scratch directory:
  1. Patch one file with GNU patch. Compare `stat` (inode, ctime, mtime) of the patched file and the others. Then remove the difference by copying the whole tree into a fresh directory and fixing the times.
  2. Build a root-owned sticky directory with a runner-owned file. Try `rm`, `mv` and edit as `runner`.
  3. In Rust, open `../etc/passwd` and a symlink that points outside with `RESOLVE_BENEATH`. Both must fail.
  4. Watch a directory. Run `sed -i` and count the events.
- **Done when:** you can say which timestamp you cannot set, and why that one still gives a patched file away.
- **Prepares:** **4.2.2** #103, **4.2.3** #104, **4.3.2** #108. Build in that order.

## Module 5: Agent link and durable store

- **Needs:** Modules 1 and 4. Python `asyncio` and SQLAlchemy basics. A local PostgreSQL (compose).
- **Read:**
  1. `realtime.asyncio-unix-connection`
  2. `realtime.asyncio-future-timeouts`
  3. `realtime.backoff-full-jitter`
  4. `persistence.durable-write-fsync`
  5. `persistence.python-hashlib`
  6. `persistence.sha256-content-addressing`
  7. `persistence.sqlalchemy-async`
  8. `persistence.sqlalchemy-for-update`
  9. `persistence.optimistic-compare-and-swap`
  10. `persistence.http-etag-if-match`
  11. `persistence.problem-json`
  12. `persistence.asyncio-tasks-timers`
  13. `persistence.trailing-debounce`
- **Exercise:** write one script with three parts.
  1. A durable write: temp file, `fsync`, `rename`, `fsync` of the directory. Kill it with `kill -9` in a loop and check that no half-written file appears.
  2. A table with a `hash` column. Run two `asyncio` tasks that save with the same `base_hash`. One must win; the other must get zero updated rows.
  3. A trailing-edge debounce that turns 1000 rapid events into one call.
- **Done when:** you can explain why a replayed save with the new hash must return 200, not 409.
- **Prepares:** **8.4.2** #213, **8.8.1** #234, **8.8.3** #236, **8.8.2** #235. Build in that order.

## Module 6: Events and the browser socket

- **Needs:** Module 5. PostgreSQL basics. Module 2 for the agent side of 4.3.7.
- **Read:**
  1. `realtime.pg-listen`
  2. `realtime.pg-notify`
  3. `realtime.outbox-pattern`
  4. `realtime.asyncpg-add-listener`
  5. `realtime.psycopg3-notifies`
  6. `realtime.pg-terminate-backend`
  7. `realtime.pg-transaction-visibility`
  8. `realtime.uuid-v7`
  9. `realtime.starlette-websocket`
  10. `realtime.asyncio-queue-bounded`
  11. `realtime.websocket-ping-pong`
  12. `security.cswsh` and `realtime.origin-check-websocket` (P0 read-ahead)
  13. `sandbox.tokio-mpsc-bounded`
  14. `sandbox.shell-command-capture`
- **Exercise:** with two `psql` sessions and one `asyncpg` listener:
  1. Show that `NOTIFY` arrives only on commit.
  2. Insert an event row and send `pg_notify` with its id in one transaction. Read the row by id in the listener.
  3. Open two transactions that take ids 1 and 2. Commit 2 before 1. Show that a reader that tracks "last id" misses id 1.
  4. Kill the listener with `pg_terminate_backend`. Reconnect and catch up by last id.
- **Done when:** you can describe the gap-free resume steps (subscribe, query, drain, dedupe) and why ids alone are not enough.
- **Prepares:** **8.4.4** #215, **8.4.1** #212, **4.3.7** #113. Build in that order.

## Module 7: The terminal path

- **Needs:** Modules 2, 3 and 6. Basic HTTP and TLS.
- **Read:**
  1. `sandbox.pty-session`
  2. `sandbox.process-groups-killpg`
  3. `sandbox.portable-pty`
  4. `sandbox.tokio-spawn-blocking`
  5. `sandbox.tokio-asyncfd`
  6. `protocol.websocket-rfc6455`
  7. `protocol.tokio-tungstenite`
  8. `sandbox.governor`
  9. `security.hmac-signed-tokens`
  10. `security.constant-time-compare`
  11. `security.jwt-jti`
  12. `security.python-secrets`
  13. `security.token-hashing-at-rest`
  14. `sandbox.docker-internal-network`
  15. `sandbox.docker-embedded-dns`
  16. `sandbox.caddy-reverse-proxy`
  17. `sandbox.caddy-forward-auth`
  18. `sandbox.caddy-stream-close-delay`
  19. `realtime.caddy-flush-interval`
  20. `realtime.tcp-nodelay`
  21. `realtime.xterm-flow-control`
- **Exercise:** two small scripts.
  1. A Python program that opens a PTY, runs `bash` in a new session, resizes it with `TIOCSWINSZ` (check with `stty size`), and kills the process group on close.
  2. A token function: HMAC sign, expiry, single-use `jti`, and a constant-time compare. Write tests for a missing, expired, reused and tampered token.
- **Done when:** you can say who consumes the single-use token (Caddy or the agent) and what happens to open terminals on a Caddy reload.
- **Prepares:** **8.7.4** #232 (pulled, terminal token only), **4.4.1** #115 (pulled), **4.4.2** #116 (pulled, terminal route only), **4.3.3** #109, **8.4.3** #214. Build in that order.

## Module 8: Agent tasks, ports and tutor tools

- **Needs:** Modules 2, 4 and 7 (process groups).
- **Read:**
  1. `sandbox.vscode-tasks`
  2. `sandbox.jsonc-parsing`
  3. `sandbox.tokio-process`
  4. `sandbox.process-groups-killpg` (again, for task stop)
  5. `sandbox.proc-net-tcp`
  6. `sandbox.procfs-crate`
  7. `sandbox.sock-diag`
  8. `sandbox.execve-argv`
  9. `sandbox.setrlimit`
  10. `sandbox.grep-searcher` (again, for in-process search)
- **Exercise:** write one Python script.
  1. Parse a `tasks.json` with comments. Order the tasks by `dependsOn`. Report a cycle as an error.
  2. Read `/proc/net/tcp` and `tcp6`. Print the listening ports. Then start `python -m http.server 5173 --bind 127.0.0.1`, and again with `0.0.0.0`, and compare.
  3. Run a command from an argv list with `RLIMIT_CPU` set. Kill the whole group after a timeout.
- **Done when:** you can say why `find` and `rg` are not safe "read-only" tools, and what you use instead.
- **Prepares:** **4.3.4** #110, **4.3.5** #111, **4.3.6** #112. Build in that order.

## Module 9: Test runs and job leases

- **Needs:** Modules 3, 5 and 8. A working Docker SDK client from Module 3.
- **Read:**
  1. `sandbox.docker-network-none`
  2. `sandbox.python-tarfile`
  3. `sandbox.defusedxml`
  4. `sandbox.junit-xml`
  5. `sandbox.asyncio-timeout`
  6. `sandbox.procrastinate-queues-locks`
  7. `persistence.procrastinate-retry`
  8. `persistence.skip-locked`
  9. `persistence.pg-advisory-locks`
  10. `persistence.fencing-token`
  11. `sandbox.docker-sdk-engine` and `sandbox.gnu-patch-reverse` (again)
- **Exercise:**
  1. Run `pytest --junitxml` in a container with `--network none` and a timeout that kills the container. Parse the file with `defusedxml`.
  2. Define one procrastinate job. `kill -9` the worker mid-job and watch the job return to the queue.
  3. Add an `attempt` check to its write, and show that a paused worker (`SIGSTOP`) cannot write after its lease ends.
- **Done when:** you can explain why the timeout must kill the container and not only the exec, and why a JUnit file from the box is not trusted alone.
- **Prepares:** **8.5.2** #218, **4.6.1** #124, **4.6.2** #125, **4.6.3** #126. Build in that order.

---

## Coverage

Each Phase 1 story appears in the module that first teaches what it needs. Build order across modules follows the study guide, section (a).

| Story | Module |
|---|---|
| 8.9.3 #242 (pulled) | 1 |
| 4.3.1 #107 | 1, 2 |
| 8.10.4 #248 (pulled) | 2 |
| 4.1.2 #97 | 3 |
| 4.2.2 #103, 4.2.3 #104, 4.3.2 #108 | 4 |
| 8.4.2 #213, 8.8.1 #234, 8.8.3 #236, 8.8.2 #235 | 5 |
| 8.4.4 #215, 8.4.1 #212, 4.3.7 #113 | 6 |
| 8.7.4 #232, 4.4.1 #115, 4.4.2 #116 (all pulled), 4.3.3 #109, 8.4.3 #214 | 7 |
| 4.3.4 #110, 4.3.5 #111, 4.3.6 #112 | 8 |
| 8.5.2 #218, 4.6.1 #124, 4.6.2 #125, 4.6.3 #126 | 9 |

## Known gaps

- The design questions in `docs/design-issues.md` (#394–#409) are parked. This path does not resolve them. Some stories, such as 4.3.3, still carry open questions in the study guide.
- Three concepts have non-primary or partial sources. See "Known gaps" in `docs/learn/README.md`.
